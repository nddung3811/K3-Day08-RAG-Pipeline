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
.stApp { background:var(--cream); color:var(--ink); font-family:'Be Vietnam Pro',sans-serif; }
[data-testid="stSidebar"] { background:#321f1a; border-right:1px solid #5d382b; }
[data-testid="stSidebar"] * { color:#fff8e9 !important; }
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
div[data-testid="stChatMessage"] { background:#fff; border:1px solid #ead9b9; border-radius:16px; margin:.6rem 0; }
.stButton button { border-radius:10px; border-color:#c99a54; }
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
    st.markdown("### Câu hỏi gợi ý")
    for i, question in enumerate(SUGGESTIONS):
        if st.button(question, key=f"suggestion_{i}", use_container_width=True):
            st.session_state.pending_query = question
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
for col, icon, title, desc in zip(cols, ["🌾", "👘", "🎏"], ["Phong tục tập quán", "Trang phục truyền thống", "Lễ hội Việt Nam"], ["Ý nghĩa, nguồn gốc và những điều nên biết", "Áo dài, áo ngũ thân và trang phục 54 dân tộc", "Nghi lễ, câu chuyện và giá trị cộng đồng"]):
    with col:
        st.markdown(f'<div class="card"><div style="font-size:1.8rem">{icon}</div><h3>{title}</h3><p>{desc}</p></div>', unsafe_allow_html=True)

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
                response = generate_with_citation(query, top_k=5)
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
