"""
RAG Evaluation Pipeline.

Sử dụng DeepEval / RAGAS / TruLens để đánh giá chất lượng RAG pipeline.
Chọn 1 framework và implement đầy đủ.

Yêu cầu:
    1. Load golden_dataset.json (≥15 Q&A pairs)
    2. Chạy RAG pipeline trên từng question
    3. Evaluate với 4 metrics: faithfulness, relevance, context_recall, context_precision
    4. So sánh A/B ít nhất 2 configs
    5. Export results ra results.md

Lưu ý rate limit nếu dùng model OpenRouter ":free": RAGAS/DeepEval gọi LLM RẤT NHIỀU LẦN
(không phải 1 lần/câu hỏi mà nhiều lần/metric/câu hỏi). Model free của OpenRouter giới hạn
50 request/ngày CHO CẢ TÀI KHOẢN (không phải theo model hay theo API key — đổi model free
khác hay tạo key mới KHÔNG reset quota). Nếu chạy full 15+ câu hỏi mà bị rate limit giữa
chừng, thử giảm xuống subset 5 câu để chạy kịp trong buổi, hoặc nạp $10 credit để mở khóa
1000 request/ngày.
"""

import json
from pathlib import Path
import sys
import asyncio
import nest_asyncio

# Khắc phục lỗi asyncio deadlock của Ragas trên Windows
nest_asyncio.apply()
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

GOLDEN_DATASET_PATH = Path(__file__).parent / "golden_dataset.json"
RESULTS_PATH = Path(__file__).parent / "results.md"


def load_golden_dataset() -> list[dict]:
    """Load golden dataset từ JSON file."""
    with open(GOLDEN_DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# =============================================================================
# Option 1: DeepEval
# =============================================================================

def evaluate_with_deepeval(rag_pipeline, golden_dataset: list[dict]) -> dict:
    """
    Evaluate RAG pipeline sử dụng DeepEval.

    pip install deepeval
    """
    # Nhóm đã chọn sử dụng RAGAS, xem hàm `evaluate_with_ragas`
    pass


# =============================================================================
# Option 2: RAGAS
# =============================================================================

def evaluate_with_ragas(rag_pipeline, golden_dataset: list[dict]) -> dict:
    """
    Evaluate RAG pipeline sử dụng RAGAS.

    pip install ragas
    """
    from ragas import evaluate
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
        context_recall,
        context_precision,
    )
    from datasets import Dataset

    eval_data = {"question": [], "answer": [], "contexts": [], "ground_truth": []}

    print("Generating answers for evaluation...")
    for item in golden_dataset:
        result = rag_pipeline.generate_with_citation(item["question"])
        eval_data["question"].append(item["question"])
        eval_data["answer"].append(result["answer"])
        eval_data["contexts"].append([c.get("content", "") for c in result["sources"]])
        eval_data["ground_truth"].append(item["expected_answer"])

    dataset = Dataset.from_dict(eval_data)
    print("Running Ragas evaluation metrics...")
    result = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_recall, context_precision],
    )
    return result


# =============================================================================
# Option 3: TruLens
# =============================================================================

def evaluate_with_trulens(rag_pipeline, golden_dataset: list[dict]) -> dict:
    """
    Evaluate RAG pipeline sử dụng TruLens.

    pip install trulens
    """
    #     rag_pipeline,
    #     app_name="UniversityServices_RAG",
    #     feedbacks=[f_faithfulness, f_relevance, f_context_relevance],
    # )
    #
    # with tru_rag as recording:
    #     for item in golden_dataset:
    #         rag_pipeline.generate_with_citation(item["question"])
    #
    # # Dashboard: from trulens.dashboard import run_dashboard; run_dashboard()
    raise NotImplementedError("Implement evaluate_with_trulens")


# =============================================================================
# A/B Comparison
# =============================================================================

def compare_configs(rag_pipeline, golden_dataset: list[dict]):
    """
    So sánh A/B giữa ít nhất 2 configs.

    Gợi ý configs để so sánh:
    - Config A: hybrid search + reranking
    - Config B: dense-only (không reranking)
    - Config C: hybrid search + PageIndex fallback
    """
    print("\n[A/B Testing] Running compare_configs...")
    # Tăng số lượng câu hỏi test lên 20 để thấy rõ sự khác biệt giữa các mô hình (Hybrid vs Dense)
    test_subset = golden_dataset[:20]
    
    configs = {
        "Config A (hybrid)": "hybrid",
        "Config B (dense-only)": "semantic",
    }
    
    print("Đang import ragas...")
    from ragas import evaluate
    from ragas.metrics import faithfulness, answer_relevancy, context_recall, context_precision
    print("Đang import datasets...")
    from datasets import Dataset
    print("Đang import langchain_openai...")
    from langchain_openai import ChatOpenAI
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from ragas.run_config import RunConfig
    import os
    
    # Set max_retries=1 để không bị kẹt retry vô tận nếu hết quota/rate limit
    # Sử dụng API của bên thứ 3 (wokushop.com)
    openai_key = os.getenv("OPENAI_API_KEY")
    eval_llm = ChatOpenAI(
        api_key=openai_key, 
        base_url="https://llm.wokushop.com/v1",
        model="gpt-4o-mini",
        max_retries=2,
        timeout=120
    )
    print("Đang khởi tạo Embeddings (Local)...")
    # Sử dụng local embeddings để tránh bị treo khi API bên thứ 3 không hỗ trợ embeddings
    eval_embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
    print("Khởi tạo xong API Client!")
    
    results = {}
    for config_name, search_method in configs.items():
        print(f"\nEvaluating {config_name}...")
        eval_data = {"question": [], "answer": [], "contexts": [], "ground_truth": []}
        for item in test_subset:
            result = rag_pipeline.generate_with_citation(item["question"], search_method=search_method)
            eval_data["question"].append(item["question"])
            eval_data["answer"].append(result["answer"])
            eval_data["contexts"].append([c.get("content", "") for c in result["sources"]])
            eval_data["ground_truth"].append(item["expected_answer"])
            
        dataset = Dataset.from_dict(eval_data)
        print(f"Bắt đầu gọi API OpenAI chấm điểm cho {config_name}...")
        eval_result = evaluate(
            dataset,
            metrics=[faithfulness, answer_relevancy, context_recall, context_precision],
            llm=eval_llm,
            embeddings=eval_embeddings,
            raise_exceptions=True
        )
        print(f"Chấm điểm xong cho {config_name}!")
        results[config_name] = eval_result
        
    return results


# =============================================================================
# Export Results
# =============================================================================

def export_results(results: dict, comparison: dict):
    """Export evaluation results to results.md"""
    content = "# RAG Evaluation Results\n\n"
    content += "## Overall Scores (Config A - Hybrid)\n\n"
    content += "| Metric | Score |\n|--------|-------|\n"
    
    if "Config A (hybrid)" in comparison:
        res_a = comparison["Config A (hybrid)"]
        content += f"| Faithfulness | {res_a.get('faithfulness', 0):.4f} |\n"
        content += f"| Answer Relevance | {res_a.get('answer_relevancy', 0):.4f} |\n"
        content += f"| Context Recall | {res_a.get('context_recall', 0):.4f} |\n"
        content += f"| Context Precision | {res_a.get('context_precision', 0):.4f} |\n"
    
    content += "\n## A/B Comparison Analysis\n\n"
    content += "| Metric | Config A (hybrid) | Config B (dense-only) |\n"
    content += "|--------|-------------------|-----------------------|\n"
    
    if "Config A (hybrid)" in comparison and "Config B (dense-only)" in comparison:
        res_a = comparison["Config A (hybrid)"]
        res_b = comparison["Config B (dense-only)"]
        metrics = ["faithfulness", "answer_relevancy", "context_recall", "context_precision"]
        for m in metrics:
            val_a = res_a.get(m, 0)
            val_b = res_b.get(m, 0)
            content += f"| {m} | {val_a:.4f} | {val_b:.4f} |\n"
            
    content += "\n**Kết luận:**\n"
    content += "> Hybrid search thường cho chỉ số Context Precision cao hơn do BM25 tìm chính xác từ khóa, trong khi Dense-only đôi khi nhạy cảm với cách dùng từ. Điểm Faithfulness phụ thuộc vào LLM Generation.\n"
    
    RESULTS_PATH.write_text(content, encoding="utf-8")
    print(f"\n✅ Đã lưu báo cáo kết quả đánh giá tại: {RESULTS_PATH}")


if __name__ == "__main__":
    golden_dataset = load_golden_dataset()
    print(f"Loaded {len(golden_dataset)} test cases")

    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    import src.task10_generation as pipeline

    print("Bắt đầu quy trình đánh giá (A/B testing)...")
    # Chúng ta chạy hàm compare_configs trước, vì nó sẽ tự evaluate
    comparison = compare_configs(pipeline, golden_dataset)
    export_results(None, comparison)
