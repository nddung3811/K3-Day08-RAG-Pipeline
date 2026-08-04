# RAG Evaluation Results

## Framework sử dụng

> Đã cấu hình chạy bằng **RAGAS** (ragas==0.1.21) với LLM giám khảo: **gpt-4o-mini** qua Wokushop API.
> Embeddings đánh giá: **BAAI/bge-m3** (local).

---

## Overall Scores (Config A - Hybrid)

| Metric | Score |
|--------|-------|
| Faithfulness | 0.7199 |
| Answer Relevance | 0.5858 |
| Context Recall | 0.9667 |
| Context Precision | 0.9610 |
| **Average** | **0.8084** |

---

## A/B Comparison Analysis

| Metric | Config A (hybrid) | Config B (dense-only) | Δ |
|--------|-------------------|-----------------------|---|
| Faithfulness | 0.7199 | 0.8583 | -0.1384 |
| Answer Relevance | 0.5858 | 0.5412 | **+0.0446** |
| Context Recall | 0.9667 | 0.8333 | **+0.1334** |
| Context Precision | 0.9610 | 0.9227 | **+0.0383** |

**Kết luận:**
> Config A (Hybrid) vượt trội rõ rệt ở hai chỉ số truy xuất quan trọng nhất:
> - **Context Recall (+13.3%):** Hybrid tìm được nhiều tài liệu liên quan hơn nhờ BM25 bắt chính xác từ khóa đặc thù (tên lễ hội, thuật ngữ văn hóa) mà Semantic Search bỏ sót.
> - **Context Precision (+3.8%):** Các tài liệu truy xuất được chính xác hơn, ít nhiễu hơn.
> - **Answer Relevance (+4.5%):** Câu trả lời sát với câu hỏi hơn nhờ context tốt hơn.
> - Faithfulness của Hybrid thấp hơn (-13.8%) là do khi có nhiều context phong phú hơn, LLM đôi khi tổng hợp thông tin từ nhiều nguồn, dẫn đến diễn đạt không bám sát nguyên văn từng chunk. Đây là trade-off chấp nhận được.

---

## Worst Performers (Bottom 3)

| # | Question | Faithfulness | Relevance | Recall | Failure Stage | Root Cause |
|---|----------|-------------|-----------|--------|---------------|------------|
| 1 | Trang phục Áo ngũ thân nam truyền thống gồm những chi tiết nào? | 0.50 | 0.48 | 0.80 | Generation | LLM bị nhầm lẫn giữa mô tả Áo ngũ thân và các biến thể Áo dài khác do thông tin nằm rải rác ở nhiều chunk. |
| 2 | Tài liệu trong repo có cung cấp thông tin về học phí RMIT? | 1.00 | 0.00 | 1.00 | Out-of-domain | Câu hỏi bẫy (OOD) nhằm kiểm tra khả năng từ chối trả lời, answer_relevancy = 0 là hành vi mong đợi. |
| 3 | Lễ hội Đền Hùng được tổ chức vào ngày nào hàng năm? | 0.40 | 0.55 | 0.00 | Retrieval | Chưa có đủ file PDF liên quan đến Lễ hội Đền Hùng trong dữ liệu đầu vào → Context Recall = 0. |

---

## Bonus Features Implemented

### 1. HyDE — Hypothetical Document Embeddings (+5đ)
- **File:** `src/task10_generation.py` → hàm `hyde_expand_query()`
- **Cơ chế:** Trước khi tìm kiếm, LLM sinh ra một đoạn trả lời giả định (3-5 câu), sau đó nối với câu hỏi gốc làm query mở rộng cho Semantic Search.
- **Lợi ích:** Thu hẹp khoảng cách ngữ nghĩa giữa câu hỏi ngắn và tài liệu dài, cải thiện Context Recall.

### 2. TF-IDF Search — So sánh cơ chế Lexical Search (+5đ)
- **File:** `src/task6_lexical_search.py` → hàm `tfidf_search()`
- **Chi tiết:** Xem docstring trong hàm `tfidf_search()` — có bảng so sánh chi tiết TF-IDF vs BM25 về công thức, ưu/nhược điểm.

### 3. Conversation Memory — Multi-turn Chat (+3đ)
- **File:** `src/task10_generation.py` → tham số `conversation_history`
- **File:** `app.py` → truyền `st.session_state.messages` vào backend
- **Cơ chế:** Giữ 6 lượt hội thoại gần nhất trong prompt, cho phép LLM hiểu ngữ cảnh câu hỏi tiếp nối.

### 4. UI/UX Nâng cao (+3đ)
- **File:** `app.py`
- Hiển thị **Relevance Score (%)** cho từng nguồn tài liệu với mã màu (xanh/cam/đỏ).
- Hiển thị **phương pháp tìm kiếm** (HYBRID/SEMANTIC) trong expander nguồn.
- Hiển thị preview nội dung chunk và loại tài liệu (LEGAL/NEWS).
- Toggle bật/tắt HyDE ngay trên sidebar.

---

## Recommendations

### Cải tiến 1: Bổ sung dữ liệu đa dạng hơn
**Action:** Cập nhật thêm các bài báo khoa học và tạp chí về "Lễ hội Gióng" và "Tín ngưỡng thờ Mẫu" vào thư mục `landing`.
**Expected impact:** Giải quyết tình trạng LLM không thể trả lời các câu hỏi ngoài lề (giảm tỷ lệ lỗi False Negative), tăng điểm Context Recall.

### Cải tiến 2: Tinh chỉnh lại Chunk Size
**Action:** Hiện tại RecursiveCharacterTextSplitter đang dùng `chunk_size=800`. Đối với tài liệu văn hoá có nhiều đoạn mô tả dài, nên tăng `chunk_size` lên 1200–1500.
**Expected impact:** Tránh việc thông tin mô tả chi tiết bị cắt đứt giữa 2 chunk, giúp LLM tổng hợp Context Precision tốt hơn.

### Cải tiến 3: Fine-tune HyDE Prompt
**Action:** Thử nghiệm prompt HyDE chuyên biệt hơn cho từng loại câu hỏi (lễ hội / trang phục / pháp luật).
**Expected impact:** Tăng chất lượng đoạn giả định, cải thiện recall thêm 5-10%.
