"""
Task 10 — Generation Có Citation.

Hướng dẫn:
    1. Chọn top_k, top_p phù hợp (giải thích lý do)
    2. Sắp xếp lại chunks sau reranking để tránh "lost in the middle"
    3. Inject context vào prompt
    4. Yêu cầu LLM trả lời có citation
    5. Nếu không đủ evidence → "I cannot verify this information"

Gợi ý LLM: OpenRouter có nhiều model gắn hậu tố ":free" không tính phí — xem
https://openrouter.ai/models?max_price=0 — phù hợp nếu chưa có credit trả phí.
Base URL: "https://openrouter.ai/api/v1", dùng chung interface với OpenAI SDK.
"""

import os
from dotenv import load_dotenv

load_dotenv()

from .task9_retrieval_pipeline import retrieve


# =============================================================================
# CONFIGURATION — Giải thích lựa chọn
# =============================================================================

# top_k: Số chunks đưa vào context
# Chọn 5 vì: đủ evidence mà không quá dài gây lost in the middle
TOP_K = 5

# top_p (nucleus sampling): Xác suất tích luỹ cho token generation
# Chọn 0.9 vì: đủ diverse nhưng không quá random
TOP_P = 0.9

# temperature: Độ ngẫu nhiên của output
# Chọn 0.3 vì: RAG cần factual, ít sáng tạo
TEMPERATURE = 0.3

# Có thể override bằng LLM_MODEL trong .env.
OPENAI_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")

# HyDE — Hypothetical Document Embeddings
# Sinh một câu trả lời giả định trước, rồi dùng nó để tìm kiếm semantic.
# Điều này giúp thu hẹp khoảng cách ngữ nghĩa giữa câu hỏi ngắn và tài liệu dài.
HYDE_ENABLED = os.getenv("HYDE_ENABLED", "true").lower() == "true"


# =============================================================================
# SYSTEM PROMPT
# =============================================================================

SYSTEM_PROMPT = """Bạn là trợ lý Nếp Việt, chuyên trả lời câu hỏi về văn hóa,
phong tục, trang phục, lễ hội và di sản Việt Nam.

Quy tắc bắt buộc:
1. Chỉ sử dụng thông tin từ context được cung cấp — KHÔNG bịa đặt
2. Mỗi khẳng định phải có trích dẫn ngay sau, ví dụ: [Tuition Fees, 2026]
3. Nếu context không đủ thông tin → trả lời: "Tôi không thể xác minh thông tin này từ nguồn hiện có"
4. Trả lời bằng tiếng Việt, có cấu trúc rõ ràng theo đoạn văn
5. Không suy luận hay mở rộng ngoài những gì được nêu trong context"""

HYDE_PROMPT = """Bạn là trợ lý chuyên về văn hóa, di sản và lễ hội Việt Nam.
Dựa vào kiến thức của bạn, hãy viết một đoạn văn ngắn (3-5 câu) trả lời câu hỏi sau.
Đoạn văn này sẽ được dùng để tìm kiếm tài liệu, nên hãy sử dụng nhiều từ khóa liên quan.
Câu hỏi: {query}
Đoạn văn giả định:"""


def _get_llm_client():
    """Return (OpenAI_client, model_name) or (None, None) if unavailable."""
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not openrouter_key and not openai_key:
        return None, None
    try:
        from openai import OpenAI
        if openrouter_key:
            return OpenAI(api_key=openrouter_key, base_url="https://openrouter.ai/api/v1"), OPENROUTER_MODEL
        else:
            # Dùng Wokushop proxy cho OpenAI key
            return OpenAI(api_key=openai_key, base_url="https://llm.wokushop.com/v1"), OPENAI_MODEL
    except Exception:
        return None, None


def hyde_expand_query(query: str) -> str:
    """
    HyDE — Hypothetical Document Embeddings.

    Thay vì tìm kiếm trực tiếp bằng câu hỏi ngắn (ví dụ: "Xòe Thái là gì?"),
    ta yêu cầu LLM sinh ra một đoạn trả lời giả định chứa nhiều từ khóa liên quan,
    rồi dùng chính đoạn văn đó làm query cho Semantic Search.

    Lợi ích:
      - Thu hẹp khoảng cách ngữ nghĩa giữa câu hỏi và tài liệu.
      - Embedding của đoạn văn dài giàu ngữ cảnh hơn câu hỏi ngắn.

    Args:
        query: Câu hỏi gốc của người dùng.

    Returns:
        Chuỗi query mở rộng = câu hỏi gốc + đoạn giả định.
    """
    if not HYDE_ENABLED:
        return query

    client, model = _get_llm_client()
    if client is None:
        return query

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": HYDE_PROMPT.format(query=query)}],
            temperature=0.7,
            max_tokens=200,
        )
        hypothetical = response.choices[0].message.content or ""
        # Nối câu hỏi gốc + đoạn giả định để embedding bao quát hơn
        return f"{query}\n\n{hypothetical.strip()}"
    except Exception:
        return query


def _fallback_answer(chunks: list[dict]) -> str:
    """Return a useful cited answer when the external LLM is unavailable."""
    if not chunks:
        return "Tôi không thể xác minh thông tin này từ nguồn hiện có."

    evidence = []
    for chunk in chunks[:3]:
        metadata = chunk.get("metadata") or {}
        source = metadata.get("source") or metadata.get("path") or "Tài liệu"
        content = " ".join((chunk.get("content") or "").strip().split())
        if content:
            evidence.append(f"- {content[:650]} [{source}]")

    if not evidence:
        return "Tôi không thể xác minh thông tin này từ nguồn hiện có."
    return "Các tư liệu phù hợp nhất mình tìm được:\n\n" + "\n\n".join(evidence)


# =============================================================================
# DOCUMENT REORDERING (tránh lost in the middle)
# =============================================================================

def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """
    Sắp xếp chunks để tránh "lost in the middle" effect.

    LLM nhớ tốt thông tin ở ĐẦU và CUỐI prompt, quên thông tin ở GIỮA.
    Strategy: đặt chunks quan trọng nhất ở đầu và cuối, kém quan trọng ở giữa.

    Input order (by score):  [1, 2, 3, 4, 5]
    Output order:            [1, 3, 5, 4, 2]
    (best first, worst in middle, second-best last)

    Args:
        chunks: List sorted by score descending (from retrieval)

    Returns:
        List reordered để maximize LLM attention.
    """
    if len(chunks) <= 2:
        return list(chunks)
    front = chunks[::2]
    back = chunks[1::2]
    return front + back[::-1]


# =============================================================================
# CONTEXT FORMATTING
# =============================================================================

def format_context(chunks: list[dict]) -> str:
    """
    Format chunks thành context string cho prompt.
    Mỗi chunk có label source để LLM có thể cite.

    Args:
        chunks: List of {'content': str, 'metadata': dict, 'score': float}

    Returns:
        Formatted context string.
    """
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        metadata = chunk.get("metadata") or {}
        source = metadata.get("source") or metadata.get("path") or f"Source {i}"
        doc_type = metadata.get("type", "unknown")
        content = (chunk.get("content") or "").strip()
        if not content:
            continue
        context_parts.append(
            f"[Document {i} | Source: {source} | Type: {doc_type}]\n{content}"
        )
    return "\n\n---\n\n".join(context_parts)


# =============================================================================
# GENERATION
# =============================================================================

def generate_with_citation(
    query: str,
    top_k: int = TOP_K,
    search_method: str = "hybrid",
    conversation_history: list[dict] | None = None,
) -> dict:
    """
    End-to-end RAG generation có citation + conversation memory.

    Pipeline:
        1. (Bonus) HyDE: sinh đoạn trả lời giả định → dùng làm query mở rộng
        2. Retrieve relevant chunks
        3. Reorder để tránh lost in the middle
        4. Format context với source labels
        5. Build prompt (system + history + context + query)
        6. Call LLM
        7. Return answer + sources

    Args:
        query: Câu hỏi của user
        top_k: Số chunks đưa vào context
        search_method: Phương pháp tìm kiếm ('hybrid', 'semantic', 'lexical', 'vectorless')
        conversation_history: Danh sách tin nhắn trước đó [{"role": ..., "content": ...}]
                              để hỗ trợ multi-turn chat (Bonus: Conversation Memory)

    Returns:
        {
            'answer': str,           # Câu trả lời có citation
            'sources': list[dict],   # Các chunks đã dùng
            'retrieval_source': str  # 'hybrid' hoặc 'pageindex'
        }
    """
    # Step 1 (Bonus): HyDE — mở rộng query bằng đoạn trả lời giả định
    expanded_query = hyde_expand_query(query)

    # Step 2: Retrieve với query đã mở rộng
    chunks = retrieve(expanded_query, top_k=top_k, search_method=search_method)

    # Step 3: Reorder để tránh lost in the middle
    reordered = reorder_for_llm(chunks)

    # Step 4: Format context
    context = format_context(reordered)

    client, model = _get_llm_client()
    if client is None:
        return {
            "answer": _fallback_answer(chunks),
            "sources": chunks,
            "retrieval_source": chunks[0].get("source", search_method) if chunks else "none",
        }

    try:
        # Step 5: Build messages với conversation memory (Bonus)
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Thêm lịch sử hội thoại (tối đa 6 lượt gần nhất để không vượt context window)
        if conversation_history:
            recent_history = conversation_history[-6:]
            for msg in recent_history:
                if msg.get("role") in ("user", "assistant"):
                    messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append(
            {"role": "user", "content": f"Context:\n{context}\n\n---\n\nQuestion: {query}"}
        )

        # Step 6: Call LLM
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=TEMPERATURE,
            top_p=TOP_P,
        )
        answer = response.choices[0].message.content or _fallback_answer(chunks)
    except Exception:
        answer = _fallback_answer(chunks)

    return {
        "answer": answer,
        "sources": chunks,
        "retrieval_source": chunks[0].get("source", search_method) if chunks else "none",
    }


if __name__ == "__main__":
    test_queries = [
        "Học phí tại RMIT Vietnam là bao nhiêu?",
        "Làm sao để đặt phòng học nhóm ở thư viện?",
        "Sinh viên quốc tế có những học bổng nào?",
    ]

    for q in test_queries:
        print(f"\n{'='*70}")
        print(f"Q: {q}")
        print("=" * 70)
        result = generate_with_citation(q)
        print(f"\nA: {result['answer']}")
        print(f"\n[Sources: {len(result['sources'])} chunks | via {result['retrieval_source']}]")
