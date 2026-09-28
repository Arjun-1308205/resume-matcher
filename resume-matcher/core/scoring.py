"""Hybrid match score: text similarity + skill overlap + experience fit."""
from __future__ import annotations

from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .skills import Profile, build_profile, education_rank

WEIGHTS = {"similarity": 0.35, "skills": 0.50, "experience": 0.15}


def tfidf_similarity(resume: str, jd: str) -> float:
    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    m = vec.fit_transform([resume, jd])
    return float(cosine_similarity(m[0], m[1])[0, 0])


_model = None


def embedding_similarity(resume: str, jd: str) -> float:
    """Semantic similarity with sentence-transformers (lazy-loaded)."""
    global _model
    from sentence_transformers import SentenceTransformer, util

    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    emb = _model.encode([resume, jd], convert_to_tensor=True)
    return float(max(0.0, util.cos_sim(emb[0], emb[1]).item()))


def skill_overlap(resume_skills: set[str], jd_skills: set[str]) -> float:
    """Share of JD skills the resume covers (more useful here than Jaccard)."""
    if not jd_skills:
        return 0.0
    return len(resume_skills & jd_skills) / len(jd_skills)


def experience_fit(resume: Profile, jd: Profile) -> float:
    parts = []
    if jd.years:
        parts.append(min(resume.years / jd.years, 1.0))
    if jd.education != "none":
        parts.append(1.0 if education_rank(resume.education) >= education_rank(jd.education) else 0.5)
    return sum(parts) / len(parts) if parts else 1.0


@dataclass
class MatchResult:
    overall: float
    similarity: float
    skills: float
    experience: float
    matched: set[str]
    missing: set[str]
    resume_profile: Profile
    jd_profile: Profile


def match(resume_text: str, jd_text: str, use_embeddings: bool = False) -> MatchResult:
    rp, jp = build_profile(resume_text), build_profile(jd_text)
    sim = (embedding_similarity if use_embeddings else tfidf_similarity)(resume_text, jd_text)
    sk = skill_overlap(rp.skills, jp.skills)
    exp = experience_fit(rp, jp)
    overall = WEIGHTS["similarity"] * sim + WEIGHTS["skills"] * sk + WEIGHTS["experience"] * exp
    return MatchResult(
        overall=overall, similarity=sim, skills=sk, experience=exp,
        matched=rp.skills & jp.skills, missing=jp.skills - rp.skills,
        resume_profile=rp, jd_profile=jp,
    )
