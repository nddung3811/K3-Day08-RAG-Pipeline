"""
Task 5 - Semantic Search Module.

Dense retrieval over the vector store built in Task 4. This module uses the
same embedding model and collection helpers from task4_chunking_indexing.py, so
query vectors and indexed chunk vectors always have matching dimensions.
"""

from __future__ import annotations

try:
    from .task4_chunking_indexing import (
        chunk_documents,
        embed_chunks,
        get_collection,
        get_embedding_model,
        index_to_vectorstore,
        load_documents,
    )
except ImportError:  # Allows: python src/task5_semantic_search.py
    from task4_chunking_indexing import (
        chunk_documents,
        embed_chunks,
        get_collection,
        get_embedding_model,
        index_to_vectorstore,
        load_documents,
    )


def _to_list(vector) -> list[float]:
    if hasattr(vector, "tolist"):
        return vector.tolist()
    return list(vector)


def _collection_count(collection) -> int:
    try:
        return int(collection.count())
    except Exception:
        return 0


def _ensure_indexed():
    """
    Return a non-empty collection when standardized markdown data is available.

    This keeps Task 5 convenient in class/demo flows: semantic_search() works
    even if the user has not manually run Task 4 yet.
    """
    collection = get_collection(reset=False)
    if _collection_count(collection) > 0:
        return collection

    documents = load_documents()
    if not documents:
        return collection

    chunks = chunk_documents(documents)
    if not chunks:
        return collection

    chunks = embed_chunks(chunks)
    return index_to_vectorstore(chunks, reset_collection=True)


def _distance_to_score(distance: float) -> float:
    # Chroma cosine distance is 1 - cosine_similarity when hnsw:space="cosine".
    score = 1.0 - float(distance)
    return round(max(0.0, min(1.0, score)), 4)


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Search chunks by semantic similarity.

    Args:
        query: User question or search query.
        top_k: Maximum number of results.

    Returns:
        List of {
            'content': str,
            'score': float,      # cosine similarity in [0, 1]
            'metadata': dict     # source, doc_type/type, chunk_index, ...
        }
        Sorted by score descending.
    """
    query = (query or "").strip()
    if not query or top_k <= 0:
        return []

    collection = _ensure_indexed()
    count = _collection_count(collection)
    if count == 0:
        return []

    model = get_embedding_model()
    query_embedding = _to_list(
        model.encode(query, normalize_embeddings=True)
    )

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, count),
        include=["documents", "metadatas", "distances"],
    )

    documents = results.get("documents", [[]])[0] or []
    metadatas = results.get("metadatas", [[]])[0] or []
    distances = results.get("distances", [[]])[0] or []

    output: list[dict] = []
    for content, metadata, distance in zip(documents, metadatas, distances):
        output.append(
            {
                "content": content,
                "score": _distance_to_score(distance),
                "metadata": metadata or {},
            }
        )

    output.sort(key=lambda item: item["score"], reverse=True)
    return output[:top_k]


if __name__ == "__main__":
    sample_query = "di sản văn hóa phi vật thể là gì"
    results = semantic_search(sample_query, top_k=5)
    for result in results:
        source = result.get("metadata", {}).get("source", "unknown")
        print(f"[{result['score']:.3f}] {source}: {result['content'][:100]}...")
