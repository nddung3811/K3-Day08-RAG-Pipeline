"""
Task 8 - PageIndex Vectorless Fallback.

PageIndex is intended as the fallback retriever when hybrid vector/BM25 search
does not have a confident semantic match. Because PageIndex needs an external
account, API key, uploaded documents, and document IDs, this module also includes
a local structural fallback over markdown sections for class demos/tests.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
PAGEINDEX_DOC_ID = os.getenv("PAGEINDEX_DOC_ID", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[\w]+", text.lower(), flags=re.UNICODE))


def _local_vectorless_search(query: str, top_k: int = 5) -> list[dict]:
    """
    Local stand-in for vectorless retrieval.

    It searches markdown sections instead of dense vectors, which approximates
    the "use document structure" idea enough for offline demos.
    """
    query_tokens = _tokenize(query)
    if top_k <= 0 or not query_tokens:
        return []

    candidates: list[dict] = []

    for md_file in sorted(STANDARDIZED_DIR.rglob("*.md")):
        if not md_file.is_file():
            continue

        content = md_file.read_text(encoding="utf-8", errors="ignore")
        sections = re.split(r"\n(?=#{1,6}\s)", content)

        for section_index, section in enumerate(sections):
            section = section.strip()
            if not section:
                continue

            section_tokens = _tokenize(section)
            overlap = len(query_tokens & section_tokens)
            if overlap == 0:
                continue

            score = overlap / max(len(query_tokens), 1)
            candidates.append(
                {
                    "content": section[:2000],
                    "score": float(score),
                    "metadata": {
                        "source": md_file.name,
                        "path": str(md_file),
                        "section_index": section_index,
                    },
                    "source": "pageindex",
                }
            )

    candidates.sort(key=lambda item: item["score"], reverse=True)
    return candidates[:top_k]


def upload_documents():
    """
    Upload documents to PageIndex.

    The exact SDK workflow can vary by PageIndex version. For the lab, record
    the returned document ID in .env as PAGEINDEX_DOC_ID after uploading.
    """
    if not PAGEINDEX_API_KEY:
        raise RuntimeError("Set PAGEINDEX_API_KEY before uploading documents")

    raise NotImplementedError(
        "Upload documents with the PageIndex dashboard/SDK, then set PAGEINDEX_DOC_ID in .env"
    )


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """
    Vectorless retrieval using PageIndex, with local fallback when not configured.

    Returns:
        List of {'content': str, 'score': float, 'metadata': dict, 'source': 'pageindex'}
    """
    if top_k <= 0:
        return []

    if not PAGEINDEX_API_KEY or not PAGEINDEX_DOC_ID:
        return _local_vectorless_search(query, top_k=top_k)

    try:
        from pageindex.client import PageIndexClient  # type: ignore
    except ImportError:
        return _local_vectorless_search(query, top_k=top_k)

    client = PageIndexClient(api_key=PAGEINDEX_API_KEY)
    response = client.submit_query(doc_id=PAGEINDEX_DOC_ID, query=query)
    retrieval_id = response.get("retrieval_id") or response.get("id")
    retrieval = client.get_retrieval(retrieval_id)

    results: list[dict] = []
    rank = 1
    for node in retrieval.get("retrieved_nodes", []):
        for group in node.get("relevant_contents", []):
            for item in group:
                content = item.get("relevant_content", "")
                if not content:
                    continue

                results.append(
                    {
                        "content": content,
                        "score": 1.0 / rank,
                        "metadata": {"section": item.get("section_title", "Unknown")},
                        "source": "pageindex",
                    }
                )
                rank += 1

    return results[:top_k]


if __name__ == "__main__":
    results = pageindex_search("tuition fee payment methods", top_k=3)
    for result in results:
        print(f"[{result['score']:.3f}] {result['content'][:100]}...")
