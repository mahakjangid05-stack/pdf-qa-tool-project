from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import tempfile
import uuid
from dotenv import load_dotenv

# ✓ IMPORT FROM OTHER FILES
from backend.pdf_processor import extract_text_from_pdf
from backend.rag_engine import keyword_search
from backend.llm_handler import ask_llm 

load_dotenv()


app = FastAPI()

# Global dictionary to store extracted text in memory
pdf_storage = {
    "text": "",
    "filename": None
}

# ==================== PYDANTIC MODELS ====================
class QuestionRequest(BaseModel):
    question: str

# ==================== API ENDPOINTS ====================

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF and extract its text"""
    try:
        # ✓ FIX: Sanitize filename (prevent path traversal)
        safe_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(tempfile.gettempdir(), safe_filename)
        
        # Save uploaded file temporarily
        with open(file_path, 'wb') as f:
            contents = await file.read()
            f.write(contents)
        
        try:
            # ✓ Call pdf_processor function
            extracted_text = extract_text_from_pdf(file_path)
            
            # Store in memory
            pdf_storage["text"] = extracted_text
            pdf_storage["filename"] = file.filename
            
            return {
                "status": "success",
                "filename": file.filename,
                "total_characters": len(extracted_text),
                "preview": extracted_text[:500]
            }
        
        finally:
            # ✓ FIX: Cleanup temp file properly (even if extraction fails)
            if os.path.exists(file_path):
                os.remove(file_path)
    
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"error": str(e)}
        )

@app.post("/ask/")
async def ask_question(req: QuestionRequest):
    """Ask a question about the uploaded PDF"""
    
    # ✓ FIX: Use Pydantic model for POST body instead of query param
    question = req.question
    
    if not pdf_storage["text"]:
        return JSONResponse(
            status_code=400,
            content={"error": "No PDF uploaded yet. Please upload a PDF first."}
        )
    
    try:
        # ✓ Call RAG_engine function
        relevant_context = keyword_search(question, pdf_storage["text"])
        if not relevant_context.strip():
            relevant_context = pdf_storage["text"][:3000]
        
        # ✓ Call llm_handler function
        answer = ask_llm(question, relevant_context)
        
        return {
            "question": question,
            "answer": answer,
            "source_file": pdf_storage["filename"],
            "context_used": relevant_context[:300]
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"error": str(e)}
        )

@app.get("/status/")
def get_status():
    """Check if PDF is loaded"""
    if pdf_storage["text"]:
        return {
            "status": "PDF loaded",
            "filename": pdf_storage["filename"],
            "total_pages": pdf_storage["text"].count("--- Page"),
            "text_length": len(pdf_storage["text"])
        }
    else:
        return {
            "status": "No PDF loaded",
            "message": "Upload a PDF using /upload-pdf/"
        }
@app.get("/")
def root():
    return {
        "message": "PDF Q&A Tool",
        "endpoints": {
            "POST /upload-pdf/": "Upload a PDF",
            "POST /ask/": "Ask a question (pass JSON body: {\"question\": \"your question\"})",
            "GET /status/": "Check loaded PDF status"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)