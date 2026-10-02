import os
import anthropic

MODEL = "claude-haiku-4-5-20251001"
NOT_FOUND = "I couldn't find this information in the uploaded document."

SYSTEM_PROMPT = (
    "You answer questions using ONLY the document excerpts provided. "
    "If the excerpts do not contain the answer, reply exactly: "
    f"'{NOT_FOUND}' Do not use outside knowledge."
)

def ask_llm(question: str, context: str) -> str:
    if not context.strip():
        return NOT_FOUND

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set. Check your .env file.")

    client = anthropic.Anthropic(api_key=api_key.strip())
    response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Document excerpts:\n{context}\n\nQuestion: {question}",
        }],
    )
    return response.content[0].text
