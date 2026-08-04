# Bài Tập Nhóm — Trợ Lý Giải Đáp Phong Tục, Trang Phục & Lễ Hội Truyền Thống

## Mục Tiêu

Sau khi hoàn thành bài cá nhân, nhóm ngồi lại để xây dựng **1 trong 2 sản phẩm**:

---

## Yêu cầu 1: Sản phẩm nhóm RAG Chatbot

Xây dựng chatbot tra cứu kiến thức văn hóa dân gian Việt Nam: ý nghĩa phong tục tập quán, trang phục truyền thống (Áo ngũ thân, Áo dài, trang phục 54 dân tộc) và các lễ hội lớn.

**Yêu cầu:**
- Giao diện chat (Streamlit / Gradio / Chainlit)
- Trả lời có citation (dựa trên Task 10)
- Hỗ trợ follow-up questions (conversation memory)
- Hiển thị source documents đã dùng

**Stack gợi ý:**
```
Chainlit/Streamlit → Retrieval (Task 9) → Generation (Task 10) → Display
```

---

## Yêu cầu 2: RAG Evaluation Pipeline

Sử dụng **1 trong 3 framework** sau để evaluate pipeline RAG của nhóm:

### Framework lựa chọn

| Framework | Cài đặt | Đặc điểm |
|-----------|---------|-----------|
| [DeepEval](https://github.com/confident-ai/deepeval) | `pip install deepeval` | Nhiều metric built-in, dễ integrate với pytest |
| [RAGAS](https://github.com/explodinggradients/ragas) | `pip install ragas` | Chuẩn industry cho RAG eval, 3 trục chính |
| [TruLens](https://github.com/truera/trulens) | `pip install trulens` | Dashboard UI, feedback functions mạnh |

### Yêu cầu Evaluation

1. **Tạo Golden Dataset** — tối thiểu 15 cặp Q&A (question, expected_answer, expected_context)
2. **Chạy evaluation** trên toàn bộ golden dataset với các metrics sau:
   - **Faithfulness** — câu trả lời có bám đúng context không?
   - **Answer Relevance** — câu trả lời có đúng câu hỏi không?
   - **Context Recall** — retriever có lấy đủ evidence không?
   - **Context Precision** — trong context lấy về, bao nhiêu % thực sự hữu ích?
3. **So sánh A/B** — chạy eval trên ít nhất 2 config khác nhau (ví dụ: có reranking vs không reranking, hoặc hybrid vs dense-only)
4. **Báo cáo** — bảng điểm + phân tích worst performers + đề xuất cải tiến

Xem code mẫu (DeepEval/RAGAS/TruLens) chi tiết trong `README.md` gốc mục "Yêu cầu 2".

### Deliverable Evaluation

- [ ] File `group_project/evaluation/golden_dataset.json` — 15+ cặp Q&A
- [ ] File `group_project/evaluation/eval_pipeline.py` — script chạy evaluation
- [ ] File `group_project/evaluation/results.md` — bảng điểm + phân tích
- [ ] So sánh A/B ít nhất 2 configs

---

## Yêu Cầu Chung

1. **Tích hợp pipeline** từ bài cá nhân của các thành viên
2. **Demo hoạt động được** trong buổi trình bày (chạy local hoặc deploy)
3. **Evaluation pipeline** chạy được và có báo cáo kết quả
4. **Code push lên repository** chung của nhóm
5. **README** mô tả kiến trúc và phân công (điền bên dưới)

---

## Kiến Trúc Hệ Thống

```
[Vẽ diagram kiến trúc ở đây]
```

---

## Phân Công Công Việc

| Thành viên | MSSV | Nhiệm vụ | Trạng thái |
|-----------|------|----------|------------|
| Vũ Hải Nam| 2A202601173|Role1: Quản lý nhóm, kiến trúc Supervisor và điều phối thuyết trình demo + Chạy RAGAS benchmark & viết báo cáo results.md. |Đã xong |
| Ong Xuân Sơn|2A202601327 | Role6: Xây dựng golden_dataset.json mở rộng (20 câu hỏi) + hỗ trợ viết báo cáo result|Đã xong |
| Nguyễn Minh Nhật| 2A202601131|Role5: Thiết kế Streamlit Chatbot app.py + Task 10 (Citation Generation) | Đã xong|
| Nguyễn Duy Dũng|2A202601505 | Role4: Task 6 (BM25 / TF-IDF) + Task 7 (RRF Reranking) + Task 8 (PageIndex Fallback)|Đã xong |
| Nguyễn Tiến Thành| 2A202601539| Role 3: Task 4 (Chunking & ChromaDB Indexing) + Task 5 (Semantic Search & HyDE)| Đã xong|
| Giang Minh Phú|2A202601729 |Role2: Phụ trách Task 1 (tải PDF chính sách) + Task 2 (crawl bài viết tin tức) + Task 3 (convert Markdown) | Đã xong|

---

## Hướng Dẫn Chạy

```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Chạy app
streamlit run app.py
# hoặc
chainlit run app.py
```

---

## Lưu ý

Hãy giữ lại repo này nếu như bạn học track 3 giai đoạn 2, chúng ta sẽ phát triển tiếp dự án lên knowledge graph để khắc phục các câu hỏi hóc búa khi có các câu hỏi khó.
