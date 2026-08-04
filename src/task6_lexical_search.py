"""
Task 6 - Lexical Search Module (BM25).

Role 4 owns this module. It provides keyword-based retrieval over the
standardized markdown corpus in data/standardized/.

BM25 is useful for exact terms such as scholarship names, course codes, amounts,
and policy titles. It complements semantic search, which is better at meaning
but can miss exact keywords.
"""

from __future__ import annotations

import re
import math
from collections import Counter
from pathlib import Path

try:
    from rank_bm25 import BM25Okapi
except ImportError:  # pragma: no cover - reported clearly at runtime.
    BM25Okapi = None


PROJECT_ROOT = Path(__file__).parent.parent
STANDARDIZED_DIR = PROJECT_ROOT / "data" / "standardized"

CORPUS: list[dict] = []
BM25_INDEX = None


class SimpleBM25:
    """Small BM25 fallback used when rank-bm25 is not installed."""

    def __init__(self, tokenized_corpus: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.tokenized_corpus = tokenized_corpus
        self.k1 = k1
        self.b = b
        self.doc_freqs = [Counter(doc) for doc in tokenized_corpus]
        self.doc_lengths = [len(doc) for doc in tokenized_corpus]
        self.avgdl = sum(self.doc_lengths) / max(len(self.doc_lengths), 1)

        document_frequency: Counter[str] = Counter()
        for doc in tokenized_corpus:
            document_frequency.update(set(doc))

        total_docs = len(tokenized_corpus)
        self.idf = {
            term: math.log(1 + (total_docs - freq + 0.5) / (freq + 0.5))
            for term, freq in document_frequency.items()
        }

    def get_scores(self, query_tokens: list[str]) -> list[float]:
        scores: list[float] = []

        for freqs, doc_len in zip(self.doc_freqs, self.doc_lengths):
            score = 0.0
            for term in query_tokens:
                tf = freqs.get(term, 0)
                if tf == 0:
                    continue

                idf = self.idf.get(term, 0.0)
                denominator = tf + self.k1 * (1 - self.b + self.b * doc_len / max(self.avgdl, 1))
                score += idf * (tf * (self.k1 + 1)) / denominator

            scores.append(score)

        return scores


def tokenize(text: str) -> list[str]:
    """Tokenize English/Vietnamese-ish text without extra NLP dependencies."""
    return re.findall(r"[\w]+", text.lower(), flags=re.UNICODE)


def load_corpus() -> list[dict]:
    """
    Load markdown documents for BM25.

    This intentionally reads standardized markdown directly so Task 6 can run
    even before ChromaDB is built. Later, the corpus can be swapped for Task 4
    chunks without changing lexical_search().
    """
    corpus: list[dict] = []

    for md_file in sorted(STANDARDIZED_DIR.rglob("*.md")):
        if not md_file.is_file():
            continue

        content = md_file.read_text(encoding="utf-8", errors="ignore").strip()
        if not content:
            continue

        doc_type = "legal" if "legal" in md_file.parts else "news"
        corpus.append(
            {
                "content": content,
                "metadata": {
                    "source": md_file.name,
                    "path": str(md_file.relative_to(PROJECT_ROOT)),
                    "type": doc_type,
                },
            }
        )

    return corpus


def build_bm25_index(corpus: list[dict]):
    """
    Build a BM25Okapi index from {'content', 'metadata'} documents.
    """
    tokenized_corpus = [tokenize(doc["content"]) for doc in corpus]
    if BM25Okapi is not None:
        return BM25Okapi(tokenized_corpus)
    return SimpleBM25(tokenized_corpus)


def get_bm25_index():
    """Return cached corpus and BM25 index, building them on first use."""
    global CORPUS, BM25_INDEX

    if BM25_INDEX is None:
        CORPUS = load_corpus()
        if not CORPUS:
            return [], None
        BM25_INDEX = build_bm25_index(CORPUS)

    return CORPUS, BM25_INDEX


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Search by exact keywords using BM25.

    Returns:
        List of {'content': str, 'score': float, 'metadata': dict}, sorted by
        score descending.
    """
    if top_k <= 0:
        return []

    corpus, bm25 = get_bm25_index()
    if not corpus or bm25 is None:
        return []

    tokenized_query = tokenize(query)
    if not tokenized_query:
        return []

    scores = bm25.get_scores(tokenized_query)
    ranked_indices = sorted(range(len(scores)), key=lambda idx: scores[idx], reverse=True)

    results: list[dict] = []
    for idx in ranked_indices[:top_k]:
        score = float(scores[idx])
        results.append(
            {
                "content": corpus[idx]["content"],
                "score": score,
                "metadata": corpus[idx]["metadata"],
            }
        )

    if results and max(result["score"] for result in results) <= 0:
        for rank, result in enumerate(results, 1):
            result["score"] = 1e-9 / rank

    return results


if __name__ == "__main__":
    results = lexical_search("tuition fee payment methods", top_k=5)
    for result in results:
        preview = result["content"][:100].encode("ascii", errors="replace").decode("ascii")
        print(f"[{result['score']:.3f}] {preview}...")
