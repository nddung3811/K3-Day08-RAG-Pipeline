# RAG Evaluation Results

## Overall Scores (Config A - Hybrid)

| Metric | Score |
|--------|-------|
| Faithfulness | 0.7199 |
| Answer Relevance | 0.5858 |
| Context Recall | 0.9667 |
| Context Precision | 0.9610 |

## A/B Comparison Analysis

| Metric | Config A (hybrid) | Config B (dense-only) |
|--------|-------------------|-----------------------|
| faithfulness | 0.7199 | 0.8583 |
| answer_relevancy | 0.5858 | 0.5412 |
| context_recall | 0.9667 | 0.8333 |
| context_precision | 0.9610 | 0.9227 |

**Kết luận:**
> Hybrid search thường cho chỉ số Context Precision cao hơn do BM25 tìm chính xác từ khóa, trong khi Dense-only đôi khi nhạy cảm với cách dùng từ. Điểm Faithfulness phụ thuộc vào LLM Generation.
