"""
Task 7 - Reranking Module.

Role 4 owns reranking. The main implementation here is RRF (Reciprocal Rank
Fusion), which merges ranked lists from semantic search and BM25 without mixing
their incompatible raw score scales.

Important: RRF scores are ranking-fusion scores, not true relevance scores. Do
not use them for PageIndex fallback thresholds in Task 9; use the original
semantic cosine score instead.
"""

from __future__ import annotations

import re
from collections import defaultdict


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[\w]+", text.lower(), flags=re.UNICODE))


def _content_key(item: dict) -> str:
    """Stable de-duplication key across dense and sparse result lists."""
    metadata = item.get("metadata", {})
    source = metadata.get("source", "")
    chunk_index = metadata.get("chunk_index", metadata.get("path", ""))
    content_prefix = item.get("content", "")[:160]
    return f"{source}:{chunk_index}:{content_prefix}"


def rerank_cross_encoder(query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
    """
    Placeholder for an external/local cross-encoder reranker.

    For this lab role, RRF is the no-key default. Keep this explicit so demos do
    not pretend an API reranker is configured.
    """
    raise NotImplementedError("Cross-encoder reranking requires a configured reranker API/model")


def rerank_mmr(
    query_embedding: list[float],
    candidates: list[dict],
    top_k: int = 5,
    lambda_param: float = 0.7,
) -> list[dict]:
    """Placeholder for MMR if the group later passes embeddings into Task 7."""
    raise NotImplementedError("MMR requires candidate embeddings")


def rerank_rrf(ranked_lists: list[list[dict]], top_k: int = 5, k: int = 60) -> list[dict]:
    """
    Merge multiple ranked lists using Reciprocal Rank Fusion.

    Formula:
        RRF(d) = sum(1 / (k + rank_r(d)))

    Args:
        ranked_lists: lists from different retrievers, already sorted best-first.
        top_k: number of fused results to return.
        k: smoothing constant, usually 60.
    """
    if top_k <= 0:
        return []

    rrf_scores: dict[str, float] = defaultdict(float)
    best_items: dict[str, dict] = {}

    for ranked_list in ranked_lists:
        for rank, item in enumerate(ranked_list, 1):
            key = _content_key(item)
            rrf_scores[key] += 1.0 / (k + rank)

            previous = best_items.get(key)
            if previous is None or item.get("score", 0) > previous.get("score", 0):
                best_items[key] = item

    sorted_keys = sorted(rrf_scores, key=lambda key: rrf_scores[key], reverse=True)

    results: list[dict] = []
    for key in sorted_keys[:top_k]:
        item = best_items[key].copy()
        item["score"] = float(rrf_scores[key])
        item.setdefault("metadata", {})
        results.append(item)

    return results


def rerank_keyword_overlap(query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
    """
    Lightweight single-list reranker for the public rerank() API.

    It combines original retrieval score, query/document token overlap, and a
    small rank prior. This makes Task 7 usable without external APIs while the
    hybrid pipeline can still call rerank_rrf() for proper multi-list fusion.
    """
    if top_k <= 0 or not candidates:
        return []

    query_tokens = _tokenize(query)
    scored: list[dict] = []

    for rank, candidate in enumerate(candidates, 1):
        item = candidate.copy()
        content_tokens = _tokenize(item.get("content", ""))
        overlap = len(query_tokens & content_tokens) / max(len(query_tokens), 1)
        original_score = float(item.get("score", 0.0) or 0.0)
        rank_bonus = 1.0 / (60 + rank)
        item["score"] = original_score + overlap + rank_bonus
        item.setdefault("metadata", {})
        scored.append(item)

    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:top_k]


def rerank(
    query: str,
    candidates: list[dict],
    top_k: int = 5,
    method: str = "rrf",
) -> list[dict]:
    """
    Unified reranking interface.

    The default method remains "rrf" for lab terminology, but when this function
    receives a single list it applies a local query-aware rerank. Use
    rerank_rrf([dense_results, sparse_results]) for true RRF fusion.
    """
    if method == "cross_encoder":
        return rerank_cross_encoder(query, candidates, top_k)
    if method == "mmr":
        raise NotImplementedError("Call rerank_mmr with query_embedding")
    if method == "rrf":
        return rerank_keyword_overlap(query, candidates, top_k)
    raise ValueError(f"Unknown rerank method: {method}")


if __name__ == "__main__":
    dummy_candidates = [
        {"content": "Tuition fee payment schedule", "score": 0.8, "metadata": {}},
        {"content": "Scholarship eligibility requirements", "score": 0.6, "metadata": {}},
        {"content": "Library study room booking guide", "score": 0.5, "metadata": {}},
    ]
    results = rerank("tuition fee payment", dummy_candidates, top_k=2)
    for result in results:
        print(f"[{result['score']:.3f}] {result['content']}")
