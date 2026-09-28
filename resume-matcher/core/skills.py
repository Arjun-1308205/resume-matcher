"""Skill, education and experience extraction driven by data/skills.csv."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SKILLS_CSV = DATA_DIR / "skills.csv"


@lru_cache(maxsize=1)
def load_taxonomy(path: str = str(SKILLS_CSV)) -> dict[str, dict]:
    """Return {canonical_skill: {"category": str, "patterns": [regex,...]}}."""
    df = pd.read_csv(path).fillna("")
    taxonomy: dict[str, dict] = {}
    for row in df.itertuples():
        names = [row.skill] + [a.strip() for a in str(row.aliases).split("|") if a.strip()]
        patterns = [
            re.compile(rf"(?<![\w+#]){re.escape(n.lower())}(?![\w+#])") for n in names
        ]
        taxonomy[row.skill.lower()] = {"category": row.category, "patterns": patterns}
    return taxonomy


def extract_skills(text: str) -> set[str]:
    lowered = text.lower()
    return {
        skill
        for skill, meta in load_taxonomy().items()
        if any(p.search(lowered) for p in meta["patterns"])
    }


def skill_category(skill: str) -> str:
    return load_taxonomy().get(skill, {}).get("category", "other")


_YEARS = re.compile(r"(\d{1,2})\s*\+?\s*(?:years?|yrs?)", re.I)
_DEGREES = {
    "phd": r"\b(ph\.?d|doctorate)\b",
    "masters": r"\b(master'?s?|m\.?sc|m\.?tech|mba)\b",
    "bachelors": r"\b(bachelor'?s?|b\.?sc|b\.?tech)\b",
    "diploma": r"\bdiploma\b",
}
_LEVEL_RANK = {"none": 0, "diploma": 1, "bachelors": 2, "masters": 3, "phd": 4}


def extract_years_experience(text: str) -> int:
    """Largest 'N years' figure found. Crude but explainable."""
    values = [int(m) for m in _YEARS.findall(text)]
    return max(values) if values else 0


def extract_education(text: str) -> str:
    lowered = text.lower()
    best = "none"
    for level, pattern in _DEGREES.items():
        if re.search(pattern, lowered) and _LEVEL_RANK[level] > _LEVEL_RANK[best]:
            best = level
    return best


def education_rank(level: str) -> int:
    return _LEVEL_RANK.get(level, 0)


@dataclass
class Profile:
    skills: set[str] = field(default_factory=set)
    years: int = 0
    education: str = "none"


def build_profile(text: str) -> Profile:
    return Profile(extract_skills(text), extract_years_experience(text), extract_education(text))
