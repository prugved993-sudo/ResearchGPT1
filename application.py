import streamlit as st
import subprocess
import os

st.set_page_config(
    page_title="ResearchGPT",
    page_icon="🧠",
    layout="wide"
)

# -------------------------
# CSS
# -------------------------
st.markdown("""
<style>

.main{
    background:#0E1117;
}

.hero{
padding:40px;
border-radius:20px;
background:linear-gradient(135deg,#1f2937,#111827);
text-align:center;
color:white;
}

.title{
font-size:55px;
font-weight:bold;
}

.subtitle{
font-size:22px;
color:#d1d5db;
}

.feature{
padding:25px;
border-radius:15px;
background:#1e293b;
text-align:center;
height:240px;
box-shadow:0 0 10px rgba(0,0,0,.2);
}

.feature h2{
color:#4ade80;
}

.footer{
text-align:center;
color:gray;
margin-top:50px;
}

</style>
""", unsafe_allow_html=True)


# -------------------------
# Session
# -------------------------
if "page" not in st.session_state:
    st.session_state.page="Home"


# -------------------------
# Sidebar
# -------------------------
with st.sidebar:

    st.title("🧠 ResearchGPT")

    option = st.radio(
        "Navigation",
        [
            "🏠 Home",
            "📄 Document QA",
            "🔍 Deep Research",
            "🎥 Video Assistant"
        ]
    )


# -------------------------
# HOME
# -------------------------
if option=="🏠 Home":

    st.markdown("""
    <div class='hero'>
    <div class='title'>ResearchGPT</div>

    <div class='subtitle'>
    One AI Platform for Research, Documents and Videos
    </div>

    <br>

    Build with Streamlit + LangChain + OpenAI + ChromaDB

    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.write("")

    c1,c2,c3=st.columns(3)

    with c1:

        st.markdown("""
        <div class='feature'>

        <h2>📄 Document QA</h2>

        Upload PDFs

        <br><br>

        Semantic Search

        <br><br>

        Ask Questions

        <br><br>

        ChromaDB Vector Store

        </div>
        """,unsafe_allow_html=True)

    with c2:

        st.markdown("""
        <div class='feature'>

        <h2>🔍 Deep Research</h2>

        AI Agent

        <br><br>

        Multi-step Reasoning

        <br><br>

        Web Research

        <br><br>

        Report Generation

        </div>
        """,unsafe_allow_html=True)

    with c3:

        st.markdown("""
        <div class='feature'>

        <h2>🎥 Video Assistant</h2>

        YouTube Support

        <br><br>

        Video Summaries

        <br><br>

        Transcript QA

        <br><br>

        AI Insights

        </div>
        """,unsafe_allow_html=True)

    st.write("")
    st.write("")

    st.subheader("✨ Features")

    st.markdown("""
- 📄 Intelligent PDF Question Answering
- 🔍 AI Deep Research Agent
- 🎥 Video Understanding Assistant
- 🧠 OpenAI Powered
- 📚 Chroma Vector Database
- ⚡ Fast Retrieval
- 🌐 Modern Dashboard
    """)

    st.write("")

    col1,col2,col3=st.columns([2,2,2])

    with col2:
        if st.button("🚀 Explore ResearchGPT",use_container_width=True):
            st.success("Select any module from the left sidebar.")

    st.markdown("""
    <div class='footer'>
    ResearchGPT © 2026
    </div>
    """,unsafe_allow_html=True)


# -------------------------
# DOCUMENT QA
# -------------------------
elif option=="📄 Document QA":

    st.title("📄 Document Question Answering")

    st.write("""
Ask questions from PDFs using semantic search and vector database.
    """)

    st.info("Run the Document QA application.")

    if st.button("▶ Launch Document QA"):

        app_path=os.path.join(
            os.getcwd(),
            "document_qa",
            "main.py"
        )

        subprocess.Popen(["streamlit","run",app_path])

        st.success("Document QA launched in a new browser tab.")


# -------------------------
# DEEP RESEARCH
# -------------------------
elif option=="🔍 Deep Research":

    st.title("🔍 Deep Research Agent")

    st.write("""
Generate AI-powered research reports using autonomous agents.
    """)

    st.info("Run Deep Research.")

    if st.button("▶ Launch Deep Research"):

        app_path=os.path.join(
            os.getcwd(),
            "deep_research",
            "app.py"
        )

        subprocess.Popen(["streamlit","run",app_path])

        st.success("Deep Research launched in a new browser tab.")


# -------------------------
# VIDEO ASSISTANT
# -------------------------
elif option=="🎥 Video Assistant":

    st.title("🎥 Video Assistant")

    st.write("""
Analyze YouTube videos, transcripts and ask questions.
    """)

    st.info("Run Video Assistant.")

    if st.button("▶ Launch Video Assistant"):

        app_path=os.path.join(
            os.getcwd(),
            "video_assistant",
            "main.py"
        )

        subprocess.Popen(["streamlit","run",app_path])

        st.success("Video Assistant launched in a new browser tab.")