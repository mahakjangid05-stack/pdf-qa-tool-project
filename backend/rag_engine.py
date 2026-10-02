import re
STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "of", "to", "in", "on", "for",
    "and", "or", "what", "which", "who", "how", "why", "when", "where", "does",
    "do", "did", "this", "that", "with", "about", "from", "it", "be", "as", "by",
}

def _tokenize(text: str) -> set:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 2}

def _chunk_text(text: str, size: int = 1000, overlap: int = 200) -> list:
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + size])
        start += size - overlap
    return chunks

def keyword_search(question: str, text: str, top_k: int = 3) -> str:
    """Return the top_k chunks that share the most keywords with the question."""
    q_words = _tokenize(question)
    if not q_words or not text:
        return ""

    scored = []
    for chunk in _chunk_text(text):
        score = len(q_words & _tokenize(chunk))
        if score > 0:
            scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return "\n\n---\n\n".join(chunk for _, chunk in scored[:top_k])
