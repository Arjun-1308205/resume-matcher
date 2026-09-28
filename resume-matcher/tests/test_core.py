import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.privacy import anonymise
from core.recommend import recommend
from core.scoring import match, skill_overlap, tfidf_similarity
from core.skills import extract_education, extract_skills, extract_years_experience

DATA = Path(__file__).resolve().parent.parent / "data"


def test_skill_extraction_handles_aliases_and_symbols():
    found = extract_skills("Worked with sklearn, Postgres and C++. Also k8s.")
    assert {"scikit-learn", "postgresql", "c++", "kubernetes"} <= found


def test_short_skill_names_do_not_match_inside_words():
    assert "r" not in extract_skills("Strong career in marketing")


def test_years_and_education():
    assert extract_years_experience("5+ years of Python") == 5
    assert extract_education("M.Tech in AI") == "masters"


def test_overlap():
    assert skill_overlap({"python"}, {"python", "sql"}) == 0.5
    assert skill_overlap({"python"}, set()) == 0.0


def test_identical_text_similarity_is_high():
    assert tfidf_similarity("python data science", "python data science") > 0.99


def test_anonymise_removes_email_and_phone():
    out = anonymise("Mail me at a.b@example.com or +91 98765 43210")
    assert "@" not in out and "98765" not in out


def test_end_to_end_on_sample_data():
    r = match((DATA / "sample_resume.txt").read_text(), (DATA / "sample_job_description.txt").read_text())
    assert 0 < r.overall < 1
    assert "docker" in r.missing and "python" in r.matched
    assert recommend(r.missing)
