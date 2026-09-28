"""Streamlit dashboard. Run from the project root:  streamlit run app/streamlit_app.py"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.parser import extract_text
from core.privacy import anonymise
from core.recommend import recommend
from core.scoring import match

DATA = Path(__file__).resolve().parent.parent / "data"

st.set_page_config(page_title="Resume Matcher", page_icon="📄", layout="wide")
st.title("📄 AI Resume Analyzer & Job Matcher")

with st.sidebar:
    st.header("Settings")
    use_emb = st.toggle("Use BERT embeddings (slower, needs sentence-transformers)", value=False)
    anon = st.toggle("Anonymise resume before scoring", value=True)
    use_sample = st.button("Load sample data")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Resume")
    upload = st.file_uploader("Upload PDF, DOCX or TXT", type=["pdf", "docx", "txt"])
    resume_text = ""
    if use_sample:
        resume_text = (DATA / "sample_resume.txt").read_text()
    if upload:
        try:
            resume_text = extract_text(upload.getvalue(), upload.name)
        except Exception as e:
            st.error(f"Could not read file: {e}")
    resume_text = st.text_area("Extracted text (editable)", resume_text, height=250)

with col2:
    st.subheader("Job description")
    default_jd = (DATA / "sample_job_description.txt").read_text() if use_sample else ""
    jd_text = st.text_area("Paste job description", default_jd, height=340)

if st.button("Analyse", type="primary", disabled=not (resume_text and jd_text)):
    text_for_scoring = anonymise(resume_text) if anon else resume_text
    try:
        with st.spinner("Scoring..."):
            result = match(text_for_scoring, jd_text, use_embeddings=use_emb)
    except ImportError:
        st.error("sentence-transformers is not installed. Turn off BERT embeddings or install it.")
        st.stop()

    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Overall match", f"{result.overall:.0%}")
    c2.metric("Text similarity", f"{result.similarity:.0%}")
    c3.metric("Skill coverage", f"{result.skills:.0%}")
    c4.metric("Experience fit", f"{result.experience:.0%}")

    fig = go.Figure(go.Bar(
        x=["Text similarity", "Skill coverage", "Experience fit"],
        y=[result.similarity, result.skills, result.experience],
    ))
    fig.update_layout(yaxis_range=[0, 1], height=300, margin=dict(t=20))
    st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)
    with left:
        st.subheader("✅ Matched skills")
        st.write(", ".join(sorted(result.matched)) or "None found")
        rp = result.resume_profile
        st.caption(f"Detected: {rp.years} yrs experience, education: {rp.education}")
    with right:
        st.subheader("❌ Missing skills")
        st.write(", ".join(sorted(result.missing)) or "None. Great coverage!")

    if result.missing:
        st.subheader("💡 Recommendations")
        st.dataframe(pd.DataFrame(recommend(result.missing)), use_container_width=True, hide_index=True)
