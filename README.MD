  # PDF Q&A Tool

A FastAPI backend that lets you upload a PDF and ask questions about it. It extracts the text, finds the most relevant passages with a keyword-based retrieval step, and passes them to an LLM to answer.

## Features
- Upload a PDF and extract its text
- Chunk-based retrieval: rare question words are weighted higher, and the top 3 chunks are returned
- Honest "not found" response when the document has nothing relevant (no made-up answers)
- Mock mode, so the whole pipeline runs without any API key or credits
- Swagger UI at `/docs` for testing

## Tech Stack
Python, FastAPI, PyPDF2, Anthropic API (optional), python-dotenv

## Setup
```bash
git clone <your-repo-url>
cd pdf-qa-tool
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create a `.env` file:
```
USE_MOCK=true
# ANTHROPIC_API_KEY=your_key_here   (only needed when USE_MOCK=false)
```

Run:
```bash
uvicorn main:app --reload
```
Open http://127.0.0.1:8000/docs

## Endpoints
| Method | Endpoint | What it does |
|---|---|---|
| POST | `/upload-pdf/` | Upload a PDF (multipart/form-data, field `file`) |
| POST | `/ask/` | Ask a question, body: `{"question": "..."}` |
| GET | `/status/` | Shows whether a PDF is loaded |
| GET | `/` | Basic info |

### Example
Request:
```json
{ "question": "Why was M. Hamel wearing a green coat and black silk cap?" }
```
Response contains `answer`, `source_file` and `context_used`.

If the document has no relevant passage, `answer` is `"Is document me iska jawab nahi mila."` and `context_used` is empty.

## Mock vs Real Mode
- `USE_MOCK=true`: returns a placeholder answer built from the retrieved context. No API calls.
- `USE_MOCK=false`: sends the question and retrieved context to the LLM.

## Known Limitations
- The PDF is stored in memory globally, so only one PDF at a time (a restart clears it)
- Keyword retrieval, no embeddings or semantic search yet

## Roadmap
- Per-document IDs (`doc_id`) for multiple PDFs
- Embedding-based retrieval
- Real LLM answers in the deployed version