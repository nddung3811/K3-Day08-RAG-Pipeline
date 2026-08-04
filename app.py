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
    radial-gradient(circle at 50% 0%, transparent 0 28px, rgba(159,45,36,.045) 29px 30px, transparent 31px 54px, rgba(211,154,52,.055) 55px 56px, transparent 57px),
    repeating-conic-gradient(from 0deg at 50% 0%, rgba(159,45,36,.035) 0deg 3deg, transparent 3deg 15deg);
  background-size:150px 150px;
  background-position:center top;
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
/* Khung nhập: dải tối + viền đồng, gợi liên tưởng khung tranh/bình phong */
div[data-testid="stChatInput"], .st-emotion-cache-jchovf.e1p9v2yr1 {
  width:100% !important; max-width:100% !important;
  background:#171922 !important;
  border:1px solid #c99a54 !important;
  border-radius:4px 22px 4px 22px !important;
  padding:10px 14px !important;
  box-shadow:0 -8px 24px rgba(37,25,20,.16) !important;
}
div[data-testid="stChatInput"]::before { content:""; position:absolute; inset:4px; pointer-events:none; border:1px solid rgba(245,208,127,.35); border-radius:2px 16px 2px 16px; }
div[data-testid="stChatInput"] > div, .st-emotion-cache-jchovf.e1p9v2yr1 > div {
  border-radius:30px !important; background:#fff !important; border:0 !important;
  padding:5px 8px 5px 20px !important; box-shadow:0 2px 10px rgba(40,25,15,.10) !important;
}
div[data-testid="stChatInput"] textarea {
  min-height:48px !important; background:#fff !important; color:#2f211b !important;
  border:0 !important; border-radius:24px !important; padding:14px 8px !important;
  font-weight:400 !important;
}
div[data-testid="stChatInput"] textarea::placeholder { color:#9b9188 !important; opacity:1; font-weight:300 !important; }
div[data-testid="stChatInput"] button {
  width:42px !important; height:42px !important; min-width:42px !important;
  border-radius:50% !important; background:#a63829 !important; color:#fff !important;
  border:0 !important; box-shadow:none !important;
}
div[data-testid="stChatInput"] button:hover { background:#82251f !important; }
div[data-testid="stChatInput"] button svg { color:#fff !important; stroke:#fff !important; }
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
                from src.task10_generation import generate_with_citation
                response = generate_with_citation(query, top_k=top_k)
                answer = response.get("answer", "Chưa có câu trả lời từ nguồn dữ liệu hiện có.")
                sources = [s.get("metadata", {}).get("source", "Tài liệu văn hóa") for s in response.get("sources", [])]
            except (NotImplementedError, ImportError):
                answer = "Mình đã nhận câu hỏi. Hãy hoàn thiện pipeline RAG ở `src/task9_retrieval_pipeline.py` và `src/task10_generation.py` để trả lời dựa trên tư liệu đã lập chỉ mục."
                sources = []
            except Exception as exc:
                answer = f"Chưa thể truy cập bộ tư liệu lúc này. Chi tiết kỹ thuật: `{exc}`"
                sources = []
        st.markdown(answer)
        if sources:
            with st.expander(f"📚 Nguồn tham khảo ({len(sources)})"):
                for source in sources:
                    st.markdown(f'<div class="source"><b>{source}</b><br><small>Tư liệu đã được truy hồi từ kho dữ liệu</small></div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})

if not st.session_state.messages:
    st.info("💬 Chọn một câu hỏi gợi ý ở thanh bên hoặc nhập câu hỏi ở ô trò chuyện bên dưới.")
