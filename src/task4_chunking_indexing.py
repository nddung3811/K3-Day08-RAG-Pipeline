"""
Task 4 - Chunking & Indexing into a Vector Store.

Current corpus: Vietnamese markdown documents about cultural heritage, beliefs,
festivals, traditional clothing, and conservation. The implementation therefore
uses multilingual embeddings, paragraph-aware chunking, and source metadata that
downstream retrieval/generation tasks can cite.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Iterable

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"


# =============================================================================
# CONFIGURATION
# =============================================================================

# Recursive chunking is a conservative fit for this dataset because PDF-converted
# legal files and HTML-converted news files do not have consistently clean
# markdown headings. It keeps paragraphs together first, then falls back to
# sentence/word boundaries.
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
CHUNKING_METHOD = "recursive"  # "recursive" | "markdown_header" | "semantic"

# BAAI/bge-m3 is multilingual and works well for Vietnamese/English retrieval.
# If the model or package is unavailable, get_embedding_model() falls back to a
# deterministic local hashing embedder so tests and local indexing still run.
EMBEDDING_MODEL = os.getenv("RAG_EMBEDDING_MODEL", "BAAI/bge-m3")
EMBEDDING_DIM = 1024

# ChromaDB is the default lab vector store: persistent, local, cosine search,
# and no Docker requirement.
VECTOR_STORE = "chromadb"
COLLECTION_NAME = "vietnamese_cultural_heritage_docs"
MIN_CHUNK_CHARS = 80

_EMBEDDING_MODEL_CACHE: Any | None = None


# =============================================================================
# TEXT LOADING AND CHUNKING
# =============================================================================

def _clean_text(text: str) -> str:
    """Normalize noisy markdown converted from PDFs/HTML without changing meaning."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_title(content: str, fallback: str) -> str:
    for line in content.splitlines():
        title = line.strip().lstrip("#").strip()
        if len(title) >= 8 and not title.isdigit():
            return title[:200]
    return fallback


def _doc_type_from_path(path: Path) -> str:
    parts = {part.lower() for part in path.parts}
    if "legal" in parts:
        return "legal"
    if "news" in parts:
        return "news"
    return "unknown"


def _stable_id(*parts: object) -> str:
    raw = "::".join(str(part) for part in parts)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def _iter_windows(text: str, chunk_size: int, chunk_overlap: int) -> Iterable[str]:
    """Fallback splitter that respects CHUNK_SIZE even without langchain."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if not 0 <= chunk_overlap < chunk_size:
        raise ValueError("chunk_overlap must be >= 0 and < chunk_size")

    start = 0
    text_len = len(text)
    while start < text_len:
        hard_end = min(start + chunk_size, text_len)
        end = hard_end

        if hard_end < text_len:
            window = text[start:hard_end]
            breakpoints = [
                window.rfind("\n\n"),
                window.rfind("\n"),
                window.rfind(". "),
                window.rfind("; "),
                window.rfind(", "),
                window.rfind(" "),
            ]
            best = max(breakpoints)
            if best >= int(chunk_size * 0.45):
                end = start + best + 1

        chunk = text[start:end].strip()
        if chunk:
            yield chunk

        if end >= text_len:
            break
        start = max(0, end - chunk_overlap)


def _fallback_split_text(text: str) -> list[str]:
    return list(_iter_windows(text, CHUNK_SIZE, CHUNK_OVERLAP))


def _split_oversized(chunk_text: str) -> list[str]:
    if len(chunk_text) <= CHUNK_SIZE:
        return [chunk_text]
    return list(_iter_windows(chunk_text, CHUNK_SIZE, CHUNK_OVERLAP))


def _split_text(text: str) -> list[str]:
    if CHUNKING_METHOD == "recursive":
        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
                separators=["\n\n", "\n", ". ", "; ", ", ", " ", ""],
            )
            splits = splitter.split_text(text)
        except ImportError:
            splits = _fallback_split_text(text)
    elif CHUNKING_METHOD == "markdown_header":
        try:
            from langchain_text_splitters import (
                MarkdownHeaderTextSplitter,
                RecursiveCharacterTextSplitter,
            )

            header_splitter = MarkdownHeaderTextSplitter(
                headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3")]
            )
            recursive = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
                separators=["\n\n", "\n", ". ", "; ", ", ", " ", ""],
            )
            splits = []
            for section in header_splitter.split_text(text):
                splits.extend(recursive.split_text(section.page_content))
        except ImportError:
            splits = _fallback_split_text(text)
    elif CHUNKING_METHOD == "semantic":
        raise RuntimeError(
            "Semantic chunking needs extra embedding-based splitters. "
            "Use CHUNKING_METHOD='recursive' for this lab setup."
        )
    else:
        raise ValueError(f"Unknown CHUNKING_METHOD: {CHUNKING_METHOD}")

    bounded: list[str] = []
    for split in splits:
        bounded.extend(_split_oversized(split.strip()))
    return [chunk for chunk in bounded if len(chunk) >= MIN_CHUNK_CHARS]


def load_documents() -> list[dict]:
    """
    Read every markdown file under data/standardized/.

    Returns:
        List of {'content': str, 'metadata': {'source': str, 'type': str, ...}}
    """
    if not STANDARDIZED_DIR.exists():
        return []

    documents: list[dict] = []
    project_root = Path(__file__).parent.parent

    for md_file in sorted(STANDARDIZED_DIR.rglob("*.md")):
        if md_file.name.startswith("."):
            continue

        content = _clean_text(md_file.read_text(encoding="utf-8", errors="replace"))
        if len(content) < MIN_CHUNK_CHARS:
            continue

        relative_path = md_file.relative_to(project_root).as_posix()
        doc_type = _doc_type_from_path(md_file)
        metadata = {
            "source": md_file.name,
            "path": relative_path,
            "type": doc_type,
            "doc_type": doc_type,
            "title": _extract_title(content, md_file.stem),
            "char_count": len(content),
        }
        documents.append({"content": content, "metadata": metadata})

    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """
    Chunk documents using the configured strategy.

    Returns:
        List of {'content': str, 'metadata': dict}; each item is one chunk.
    """
    chunks: list[dict] = []

    for doc in documents:
        content = _clean_text(doc.get("content", ""))
        if not content:
            continue

        splits = _split_text(content)
        for index, chunk_text in enumerate(splits):
            metadata = {
                **doc.get("metadata", {}),
                "chunk_index": index,
                "total_chunks": len(splits),
            }
            metadata["chunk_id"] = _stable_id(
                metadata.get("path", metadata.get("source", "")),
                index,
            )[:16]
            chunks.append({"content": chunk_text, "metadata": metadata})

    return chunks


# =============================================================================
# EMBEDDING AND VECTOR STORE
# =============================================================================

class HashingEmbeddingModel:
    """Deterministic local fallback with the same encode() shape as SentenceTransformer."""

    def __init__(self, dimension: int = EMBEDDING_DIM):
        self.dimension = dimension

    def encode(
        self,
        sentences: str | list[str],
        show_progress_bar: bool = False,
        normalize_embeddings: bool = True,
        **_: Any,
    ):
        import numpy as np

        single_input = isinstance(sentences, str)
        texts = [sentences] if single_input else list(sentences)
        vectors = np.vstack([self._encode_one(text) for text in texts])

        if normalize_embeddings:
            norms = np.linalg.norm(vectors, axis=1, keepdims=True)
            vectors = vectors / np.maximum(norms, 1e-12)

        return vectors[0] if single_input else vectors

    def _encode_one(self, text: str):
        import numpy as np

        vector = np.zeros(self.dimension, dtype="float32")
        tokens = re.findall(r"\w+", text.lower(), flags=re.UNICODE)
        features = tokens[:]

        for token in tokens:
            if len(token) >= 4:
                features.extend(token[i:i + 4] for i in range(len(token) - 3))

        if not features:
            return vector

        for feature in features:
            digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
            index = int.from_bytes(digest[:4], "little") % self.dimension
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        return vector


def _cosine_distance(left: list[float], right: list[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = sum(a * a for a in left) ** 0.5
    right_norm = sum(b * b for b in right) ** 0.5
    if left_norm == 0 or right_norm == 0:
        return 1.0
    similarity = dot / (left_norm * right_norm)
    similarity = max(-1.0, min(1.0, similarity))
    return 1.0 - similarity


class LocalVectorCollection:
    """
    Minimal persistent fallback when chromadb is not installed.

    It intentionally mirrors the Chroma methods used in this lab: upsert(),
    query(), and count(). Install chromadb to use the real vector database.
    """

    def __init__(self, path: Path, reset: bool = False):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if reset and self.path.exists():
            self.path.unlink()

    def _load(self) -> dict[str, dict]:
        if not self.path.exists():
            return {}
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return {record["id"]: record for record in data.get("records", [])}

    def _save(self, records: dict[str, dict]) -> None:
        payload = {"collection": COLLECTION_NAME, "records": list(records.values())}
        self.path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def upsert(
        self,
        ids: list[str],
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict],
    ) -> None:
        records = self._load()
        for item_id, document, embedding, metadata in zip(
            ids, documents, embeddings, metadatas
        ):
            records[item_id] = {
                "id": item_id,
                "document": document,
                "embedding": embedding,
                "metadata": metadata,
            }
        self._save(records)

    def query(
        self,
        query_embeddings: list[list[float]],
        n_results: int = 10,
        include: list[str] | None = None,
    ) -> dict:
        records = list(self._load().values())
        include = include or ["documents", "metadatas", "distances"]
        output = {"ids": []}

        if "documents" in include:
            output["documents"] = []
        if "metadatas" in include:
            output["metadatas"] = []
        if "distances" in include:
            output["distances"] = []

        for query_embedding in query_embeddings:
            scored = sorted(
                records,
                key=lambda record: _cosine_distance(
                    query_embedding,
                    record["embedding"],
                ),
            )[:n_results]

            output["ids"].append([record["id"] for record in scored])
            if "documents" in include:
                output["documents"].append([record["document"] for record in scored])
            if "metadatas" in include:
                output["metadatas"].append([record["metadata"] for record in scored])
            if "distances" in include:
                output["distances"].append([
                    _cosine_distance(query_embedding, record["embedding"])
                    for record in scored
                ])

        return output

    def count(self) -> int:
        return len(self._load())


def get_embedding_model():
    """Return the embedding model shared by indexing and semantic search."""
    global _EMBEDDING_MODEL_CACHE
    if _EMBEDDING_MODEL_CACHE is not None:
        return _EMBEDDING_MODEL_CACHE

    if os.getenv("RAG_FORCE_HASH_EMBEDDINGS", "").lower() in {"1", "true", "yes"}:
        _EMBEDDING_MODEL_CACHE = HashingEmbeddingModel()
        return _EMBEDDING_MODEL_CACHE

    try:
        from sentence_transformers import SentenceTransformer

        _EMBEDDING_MODEL_CACHE = SentenceTransformer(EMBEDDING_MODEL)
    except Exception as exc:
        print(
            f"Warning: cannot load '{EMBEDDING_MODEL}' ({exc}). "
            "Using local hashing embeddings instead."
        )
        _EMBEDDING_MODEL_CACHE = HashingEmbeddingModel()

    return _EMBEDDING_MODEL_CACHE


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """
    Embed every chunk using the configured model.

    Returns:
        The same chunk dicts with an added 'embedding': list[float] key.
    """
    if not chunks:
        return []

    model = get_embedding_model()
    texts = [chunk["content"] for chunk in chunks]
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        normalize_embeddings=True,
    )

    for chunk, embedding in zip(chunks, embeddings):
        chunk["embedding"] = embedding.tolist()

    return chunks


def get_collection(reset: bool = False):
    """Open the persistent ChromaDB collection used by Task 4 and Task 5."""
    if VECTOR_STORE != "chromadb":
        raise ValueError("This implementation supports ChromaDB only.")

    try:
        import chromadb
    except ImportError as exc:
        print(
            f"Warning: chromadb is not installed ({exc}). "
            "Using local JSON vector store fallback."
        )
        return LocalVectorCollection(
            CHROMA_DIR / f"{COLLECTION_NAME}.json",
            reset=reset,
        )

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def index_to_vectorstore(chunks: list[dict], reset_collection: bool = True):
    """Save chunks to the configured vector store."""
    if not chunks:
        raise ValueError("No chunks to index.")

    if any("embedding" not in chunk for chunk in chunks):
        chunks = embed_chunks(chunks)

    collection = get_collection(reset=reset_collection)
    ids = [
        f"{chunk['metadata']['chunk_id']}_{chunk['metadata']['chunk_index']:04d}"
        for chunk in chunks
    ]
    metadatas = [
        {
            key: value
            for key, value in chunk["metadata"].items()
            if isinstance(value, (str, int, float, bool)) and value is not None
        }
        for chunk in chunks
    ]

    collection.upsert(
        ids=ids,
        documents=[chunk["content"] for chunk in chunks],
        embeddings=[chunk["embedding"] for chunk in chunks],
        metadatas=metadatas,
    )
    return collection


def run_pipeline():
    """Run the full pipeline: load -> chunk -> embed -> index."""
    print("=" * 50)
    print("Task 4: Chunking & Indexing")
    print(f"  Chunking: {CHUNKING_METHOD} (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    print(f"  Embedding: {EMBEDDING_MODEL} (dim={EMBEDDING_DIM})")
    print(f"  Vector Store: {VECTOR_STORE}")
    print("=" * 50)

    docs = load_documents()
    print(f"\nLoaded {len(docs)} documents")

    chunks = chunk_documents(docs)
    print(f"Created {len(chunks)} chunks")

    chunks = embed_chunks(chunks)
    print(f"Embedded {len(chunks)} chunks")

    collection = index_to_vectorstore(chunks)
    print(f"Indexed to vector store: {collection.count()} chunks in {CHROMA_DIR}")


if __name__ == "__main__":
    run_pipeline()
