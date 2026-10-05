import re
import math
from collections import Counter

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
    """Return the top_k chunks, scoring rare question words higher."""
    q_words = _tokenize(question)
    if not q_words or not text:
        return ""

    chunks = _chunk_text(text)
    chunk_tokens = [_tokenize(c) for c in chunks]
    n = len(chunks)

    # har word kitne chunks mein aata hai
    df = Counter()
    for toks in chunk_tokens:
        df.update(toks)

    scored = []
    for i, (chunk, toks) in enumerate(zip(chunks, chunk_tokens)):
        matched = q_words & toks
        if not matched:
            continue
        score = sum(math.log(n / df[w]) + 1 for w in matched)
        scored.append((score, i, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = sorted(scored[:top_k], key=lambda x: x[1])  # document order
    return "\n\n---\n\n".join(chunk for _, _, chunk in top)


