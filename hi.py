from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import PyPDF2
import os
import tempfile
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

app = FastAPI()

# Global dictionary to store extracted text in memory
pdf_storage = {
    "text": "",
    "filename": None
}

client = Anthropic()


load_dotenv()

pdf_storage={
    "text":"",
    "filename":none
}
app =fastapi()

clinet = anthriopic()

# pdf_extraction
# ==================== PDF EXTRACTION ====================
def extract_text_from_pdf(file_path: str) -> str:
    """Extract all text from a PDF using PyPDF2"""
    extracted_text = ""
     
    with open(file_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        print(f"Total pages: {len(reader.pages)}")
        
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            extracted_text += f"\n--- Page {page_num + 1} ---\n{text}"
    
    return extracted_text

# ==================== KEYWORD SEARCH ====================
def keyword_search(query: str, text: str) -> str:
    """Simple keyword search in extracted text"""
    query_lower = query.lower()
    lines = text.split('\n')
    
    relevant_lines = []
    for i, line in enumerate(lines):
        if query_lower in line.lower():
            relevant_lines.append(line)
    
    if relevant_lines:
        return "\n".join(relevant_lines[:10])  # Top 10 matches
    else:
        return "No relevant text found for this query."

                     
# ==================== API ENDPOINTS ====================
@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF and extract its text"""
    try:
        # Save uploaded file temporarily (works on all OS)
        file_path = os.path.join(tempfile.gettempdir(), file.filename)
        
        with open(file_path, 'wb') as f:
            contents = await file.read()
            f.write(contents)
        
        # Extract text    
        extracted_text = extract_text_from_pdf(file_path)
        
        # Store in memory
        pdf_storage["text"] = extracted_text
        pdf_storage["filename"] = file.filename
        
        # Cleanup temp file
        os.remove(file_path)
        
        return { 
            "filename": file.filename,
            "total_characters": len(extracted_text),
            "preview": extracted_text[:500]
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"error": str(e)}
        )


@app.post("/ask/")
async def ask_question(question: str):
    """Ask a question about the uploaded PDF"""# this time you ask about u-pload_pdf and show your answer
   
    if not pdf_storage["text"]:
        return JSONResponse(
            status_code=400,
            content={"error": "No PDF uploaded yet. Please upload a PDF first."}
        )
    
    try:
        # Step 1: Do keyword search to get relevant context
        relevant_context = keyword_search(question, pdf_storage["text"])
        
        # Step 2: Use Anthropic API for smart Q&A
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": f"""You are a helpful assistant answering questions about a document.

Question: {question}

Relevant text from the document:
{relevant_context}

Based on the above text, answer the question concisely. If the answer is not in the provided text, say "This information is not available in the document."
"""
                }
            ]
        )
        
        answer = response.content[0].text
        
        return {
            "question": question,
            "answer": answer,
            "source_file": pdf_storage["filename"],
            "context_used": relevant_context[:300]  # Show preview of context
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

# ==================== ROOT ====================
@app.get("/")
def root():
    return {
        "message": "PDF Q&A Tool",
        "endpoints": {
            "POST /upload-pdf/": "Upload a PDF",
            "POST /ask/": "Ask a question (pass 'question' as query param)",
            "GET /status/": "Check loaded PDF status"
        }
    }
 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
