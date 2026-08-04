"""Trợ lý văn hóa Việt Nam — Streamlit UI.

Chạy bằng: streamlit run app.py
Backend RAG được gọi qua ``src.task10_generation`` khi đã implement.
"""

from pathlib import Path
import sys

import streamlit as st
from dotenv import load_dotenv

load_dotenv()
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

st.set_page_config(
    page_title="Nếp Việt · Trợ lý văn hóa",
    page_icon="🏮",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700&display=swap');
:root { --ink:#2f211b; --red:#9f2d24; --gold:#d39a34; --cream:#fff9ed; }
.stApp { background:var(--cream) !important; color:var(--ink) !important; font-family:'Be Vietnam Pro',sans-serif; }
[data-testid="stAppViewContainer"], [data-testid="stMain"] { background:var(--cream) !important; }
[data-testid="stMainBlockContainer"], .stMainBlockContainer { 
  background-color:var(--cream) !important;
  background-image:
    linear-gradient(rgba(255,249,237,.88), rgba(255,249,237,.92)),
    url("https://free.vector6.com/wp-content/uploads/2026/07/E269-vector-trong-dong.jpg"),
    radial-gradient(circle at 50% 0%, transparent 0 28px, rgba(159,45,36,.045) 29px 30px, transparent 31px 54px, rgba(211,154,52,.055) 55px 56px, transparent 57px),
    repeating-conic-gradient(from 0deg at 50% 0%, rgba(159,45,36,.035) 0deg 3deg, transparent 3deg 15deg);
  background-size:cover, 900px auto, 150px 150px, 150px 150px;
  background-position:center, center 80px, center top, center top;
  background-repeat:no-repeat, no-repeat, repeat, repeat;
  background-attachment:fixed;
}
[data-testid="stMain"] p, [data-testid="stMain"] label, [data-testid="stMain"] span { color:var(--ink); }
[data-testid="stSidebar"] { background:#321f1a; border-right:1px solid #5d382b; }
[data-testid="stSidebar"] * { color:#fff8e9 !important; }
[data-testid="stSidebar"] button p { color:#fff8e9 !important; }
[data-testid="stSidebar"] .stButton button { background:#fff5df !important; border:1px solid #d39a34 !important; color:#3b2921 !important; text-align:left !important; }
[data-testid="stSidebar"] .stButton button p { color:#3b2921 !important; }
[data-testid="stSidebar"] .stButton button:hover { background:#f5dcae !important; border-color:#a63829 !important; }
.hero { padding:2.2rem 2.5rem; border-radius:24px; background:linear-gradient(120deg,#681d1a 0%,#a63829 55%,#d48e31 150%); color:white; box-shadow:0 10px 28px #8e483022; }
.hero h1 { font-family:'Playfair Display',serif; font-size:3rem; margin:0 0 .4rem; color:#fff9ed; }
.hero p { max-width:730px; font-size:1.06rem; margin:0; color:#ffeac0; }
.eyebrow { color:#f3ca74; letter-spacing:.12em; text-transform:uppercase; font-size:.75rem; font-weight:700; }
.card { background:white; border:1px solid #ead9b9; border-radius:16px; padding:1.15rem; height:100%; box-shadow:0 4px 14px #8e483010; }
.card h3 { margin:.2rem 0 .4rem; color:var(--red); font-size:1.05rem; }
.card p { color:#6c5849; font-size:.9rem; margin:0; }
.section-title { font-family:'Playfair Display',serif; color:var(--red); font-size:1.55rem; margin:1.8rem 0 .8rem; }
.source { border-left:4px solid var(--gold); background:#fffaf0; padding:.75rem 1rem; border-radius:0 10px 10px 0; margin:.5rem 0; }
.source small { color:#80684f; }
.ao-dai-logo { width:48px; height:48px; display:flex; align-items:center; justify-content:center; border-radius:50%; background:#fff1d2; color:#a63829; font-size:2rem; line-height:1; }
div[data-testid="stChatMessage"] { background:#fff !important; border:1px solid #ead9b9; border-radius:16px; margin:.6rem 0; }
div[data-testid="stChatMessage"] p, div[data-testid="stChatMessage"] span, div[data-testid="stChatMessage"] li { color:#2f211b !important; }
/* Khung nhập "Rồng ôm Minh Châu": line-art Lý–Trần + input hiện đại */
div[data-testid="stChatInput"], .st-emotion-cache-jchovf.e1p9v2yr1 {
  position:relative !important;
  isolation:isolate;
  width:100% !important; max-width:100% !important;
  overflow:visible !important;
  background:
    radial-gradient(circle at 8% 20%, rgba(211,154,52,.13), transparent 22%),
    radial-gradient(circle at 92% 80%, rgba(159,45,36,.13), transparent 24%),
    linear-gradient(105deg,#12131a 0%,#1c1a1c 54%,#241916 100%) !important;
  border:1px solid rgba(211,154,52,.68) !important;
  border-radius:10px 28px 10px 28px !important;
  padding:15px 20px !important;
  box-shadow:0 -8px 28px rgba(37,25,20,.18), inset 0 0 24px rgba(211,154,52,.06) !important;
}
/* Một nét liền tạo đầu rồng bên trái, thân vờn mây và đuôi cuộn bên phải. */
div[data-testid="stChatInput"]::before {
  content:"";
  position:absolute;
  z-index:-1;
  inset:-13px -10px -11px -12px;
  pointer-events:none;
  opacity:.72;
  background:center/100% 100% no-repeat url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 118' preserveAspectRatio='none'%3E%3Cg fill='none' stroke='%23d6a44f' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M66 42C42 18 27 20 17 35c13-5 22-1 27 7-18-3-31 6-35 19 14-8 27-6 36 2-13 4-20 13-21 25 11-9 24-10 36-4 10 5 17 14 27 18H1108c20 0 34-8 43-21 8-12 10-25 2-34-5-6-15-6-20 0-7 8-1 19 9 18 13-1 24-13 21-27-3-17-18-27-33-24-15 3-25 17-23 31 2 17 17 28 35 27 24-1 40-23 36-46'/%3E%3Cpath d='M57 48c11-18 25-25 44-20-9 4-14 10-15 19 12-10 27-11 42-4-13 2-22 9-27 20 17-8 33-5 48 9M49 62c14 0 25 7 31 21M68 41c-8-13-6-24 4-34 1 12 7 20 18 24M1126 81c18 10 37 9 55-3-6 13-16 23-31 29 13 2 25-1 36-9-4 11-13 19-27 24M1161 48c13-8 23-20 27-36 5 14 3 27-5 39'/%3E%3Ccircle cx='62' cy='51' r='2.8' fill='%23efd083' stroke='none'/%3E%3Cpath opacity='.55' d='M92 90c125-12 230-12 355 0s230 12 355 0 214-12 329-1' stroke-dasharray='2 12'/%3E%3C/g%3E%3C/svg%3E");
  filter:drop-shadow(0 1px 3px rgba(211,154,52,.22));
}
/* Quầng sáng nhẹ của "minh châu" phía sau ô nhập. */
div[data-testid="stChatInput"]::after {
  content:"";
  position:absolute;
  z-index:-1;
  inset:9px 13px;
  border-radius:999px;
  background:rgba(255,244,214,.18);
  filter:blur(10px);
  pointer-events:none;
}
div[data-testid="stChatInput"] > div, .st-emotion-cache-jchovf.e1p9v2yr1 > div {
  border-radius:999px !important;
  background:linear-gradient(180deg,#fff 0%,#fffaf1 100%) !important;
  border:1px solid rgba(242,216,162,.92) !important;
  padding:5px 8px 5px 22px !important;
  box-shadow:0 3px 14px rgba(11,8,6,.24), inset 0 1px 0 #fff !important;
}
div[data-testid="stChatInput"] textarea {
  min-height:48px !important; background:transparent !important; color:#2f211b !important;
  border:0 !important; border-radius:24px !important; padding:14px 8px !important;
  font-weight:400 !important;
}
div[data-testid="stChatInput"] textarea::placeholder { color:#9b9188 !important; opacity:.92; font-weight:300 !important; }
div[data-testid="stChatInput"] button {
  width:42px !important; height:42px !important; min-width:42px !important;
  border-radius:50% !important;
  background:radial-gradient(circle at 35% 30%,#c95743 0%,#a63829 52%,#762018 100%) !important;
  color:#fff !important;
  border:1px solid rgba(255,231,185,.65) !important;
  box-shadow:0 2px 8px rgba(117,28,20,.38), inset 0 1px 2px rgba(255,255,255,.32) !important;
  transition:transform .18s ease, box-shadow .18s ease, filter .18s ease !important;
}
div[data-testid="stChatInput"] button:hover {
  transform:scale(1.06);
  filter:saturate(1.12) brightness(1.04);
  box-shadow:0 0 0 4px rgba(201,154,84,.16), 0 4px 12px rgba(117,28,20,.42) !important;
}
div[data-testid="stChatInput"] button svg { color:#fff !important; stroke:#fff !important; }
@media (max-width:700px) {
  div[data-testid="stChatInput"] { padding:12px 12px !important; border-radius:8px 22px 8px 22px !important; }
  div[data-testid="stChatInput"]::before { inset:-8px -5px; opacity:.52; }
}
.stAlert p { color:#2f211b !important; }
.stButton button { border-radius:10px; border-color:#c99a54; }
.stButton button p { color:#2f211b !important; }
</style>
""", unsafe_allow_html=True)

TOPICS = ["Tất cả chủ đề", "Phong tục tập quán", "Trang phục truyền thống", "Lễ hội Việt Nam"]
SUGGESTIONS = [
    "Ý nghĩa của tục xông đất đầu năm và những điều kiêng kỵ trong ngày Tết là gì?",
    "Áo ngũ thân nam gồm những chi tiết nào và khác gì Áo dài tân thời?",
    "Lễ hội Gióng có ý nghĩa lịch sử và nghi thức tiêu biểu nào?",
    "Trang phục truyền thống của các dân tộc Việt Nam có điểm gì đặc sắc?",
]

with st.sidebar:
    st.markdown("# 🏮 Nếp Việt")
    st.caption("Tra cứu phong tục, trang phục và lễ hội truyền thống Việt Nam")
    st.divider()
    st.markdown("### Khám phá theo chủ đề")
    topic = st.selectbox("Chủ đề", TOPICS, label_visibility="collapsed")
    region = st.selectbox("Vùng văn hóa", ["Tất cả vùng miền", "Bắc Bộ", "Trung Bộ", "Nam Bộ", "Các dân tộc Việt Nam"])
    st.divider()
    st.markdown("### ⚙️ Cài đặt tham số")
    top_k = st.slider(
        "Số tài liệu tham khảo (top_k)",
        min_value=1,
        max_value=10,
        value=5,
        help="Số đoạn tài liệu được truy hồi để tạo câu trả lời.",
    )
    search_method = st.selectbox(
        "Phương pháp tìm kiếm",
        options=["hybrid", "semantic", "lexical", "vectorless"],
        format_func=lambda value: {
            "hybrid": "🔀 Hybrid (Semantic + BM25)",
            "semantic": "🧠 Semantic / Dense",
            "lexical": "🔤 Lexical / BM25",
            "vectorless": "🌳 Vectorless / PageIndex",
        }[value],
        help="Chọn cách truy hồi tài liệu trước khi tạo câu trả lời.",
    )
    use_hyde = st.toggle(
        "💡 HyDE (Query Expansion)",
        value=True,
        help="Bật Hypothetical Document Embeddings: sinh câu trả lời giả định để tìm kiếm chính xác hơn.",
    )
    st.caption(f"Đang dùng **{top_k}** tài liệu cho mỗi câu hỏi")
    st.divider()
    st.markdown("### Câu hỏi gợi ý")
    for i, question in enumerate(SUGGESTIONS):
        if st.button(question, key=f"suggestion_{i}", use_container_width=True):
            st.session_state.pending_query = question
    st.divider()
    if st.button("🗑️ Xóa cuộc trò chuyện", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_query = None
        st.rerun()
    st.divider()
    st.caption("Nguồn định hướng")
    st.caption("Viện Nghiên cứu Văn hóa · Sách Văn hóa Dân gian Việt Nam · Hồ sơ Di sản Văn hóa Phi vật thể")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

st.markdown("""
<div class="hero">
  <div class="eyebrow">Di sản · Bản sắc · Ký ức</div>
  <h1>Hiểu hơn về Nếp Việt</h1>
  <p>Trợ lý giải đáp phong tục, trang phục và lễ hội truyền thống Việt Nam — từ những nghi lễ thân thuộc trong đời sống đến di sản văn hóa của 54 dân tộc.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-title">Hôm nay bạn muốn tìm hiểu điều gì?</div>', unsafe_allow_html=True)
cols = st.columns(3)
ao_dai_logo = '<div class="ao-dai-logo" title="Áo dài Việt Nam">👘</div>'
cards = [
    ("🌾", "Phong tục tập quán", "Ý nghĩa, nguồn gốc và những điều nên biết"),
    (ao_dai_logo, "Trang phục truyền thống", "Áo dài, áo ngũ thân và trang phục 54 dân tộc"),
    ("🎏", "Lễ hội Việt Nam", "Nghi lễ, câu chuyện và giá trị cộng đồng"),
]
for col, (icon, title, desc) in zip(cols, cards):
    with col:
        st.markdown(f'<div class="card"><div style="height:48px;display:flex;align-items:center;font-size:1.8rem">{icon}</div><h3>{title}</h3><p>{desc}</p></div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">Cuộc trò chuyện</div>', unsafe_allow_html=True)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander(f"📚 Nguồn tham khảo ({len(message['sources'])})"):
                for source in message["sources"]:
                    st.markdown(f'<div class="source"><b>{source}</b><br><small>Hồ sơ di sản · Tài liệu văn hóa dân gian</small></div>', unsafe_allow_html=True)

query = st.chat_input("Ví dụ: Ý nghĩa của tục xông đất đầu năm là gì?") or st.session_state.pending_query
if query:
    st.session_state.pending_query = None
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)
    with st.chat_message("assistant"):
        with st.spinner("Đang tra cứu tư liệu văn hóa…"):
            try:
                import os as _os
                _os.environ["HYDE_ENABLED"] = "true" if use_hyde else "false"
                from src.task10_generation import generate_with_citation
                # Bonus: Conversation Memory — truyền lịch sử hội thoại
                response = generate_with_citation(
                    query,
                    top_k=top_k,
                    search_method=search_method,
                    conversation_history=st.session_state.messages,
                )
                answer = response.get("answer", "Chưa có câu trả lời từ nguồn dữ liệu hiện có.")
                sources_data = response.get("sources", [])
                retrieval_source = response.get("retrieval_source", "unknown")
            except (NotImplementedError, ImportError):
                answer = "Mình đã nhận câu hỏi. Hãy hoàn thiện pipeline RAG ở `src/task9_retrieval_pipeline.py` và `src/task10_generation.py` để trả lời dựa trên tư liệu đã lập chỉ mục."
                sources_data = []
                retrieval_source = "none"
            except Exception as exc:
                answer = f"Chưa thể truy cập bộ tư liệu lúc này. Chi tiết kỹ thuật: `{exc}`"
                sources_data = []
                retrieval_source = "error"
        st.markdown(answer)
        # Bonus UI: Hiển thị nguồn tài liệu có điểm số và phương pháp tìm kiếm
        if sources_data:
            source_names = []
            with st.expander(f"📚 Nguồn tham khảo ({len(sources_data)}) • {retrieval_source.upper()}"):
                for i, src in enumerate(sources_data, 1):
                    meta = src.get("metadata", {})
                    name = meta.get("source", "Tài liệu")
                    score = src.get("score", 0)
                    doc_type = meta.get("type", "")
                    source_names.append(name)
                    # Tạo thanh relevance score bằng CSS
                    score_pct = min(int(score * 100), 100)
                    score_color = "#2e7d32" if score_pct >= 70 else "#ed6c02" if score_pct >= 40 else "#d32f2f"
                    content_preview = (src.get("content", ""))[:200].strip()
                    st.markdown(f'''
<div class="source">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
    <b>{i}. {name}</b>
    <span style="background:{score_color};color:white;padding:2px 8px;border-radius:12px;font-size:.75rem">
      Relevance: {score_pct}%
    </span>
  </div>
  <small style="color:#80684f">🎯 {doc_type.upper()} • {content_preview}…</small>
</div>''', unsafe_allow_html=True)
        else:
            source_names = []
    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": source_names if sources_data else []})

if not st.session_state.messages:
    st.info("💬 Chọn một câu hỏi gợi ý ở thanh bên hoặc nhập câu hỏi ở ô trò chuyện bên dưới.")
