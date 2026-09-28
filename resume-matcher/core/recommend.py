"""Turn missing skills into suggestions, driven by data/recommendations.csv."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .skills import skill_category

REC_CSV = Path(__file__).resolve().parent.parent / "data" / "recommendations.csv"


def recommend(missing: set[str]) -> list[dict]:
    recs = pd.read_csv(REC_CSV).fillna("").set_index("skill").to_dict("index")
    out = []
    for skill in sorted(missing):
        info = recs.get(skill, {})
        out.append({
            "skill": skill,
            "category": skill_category(skill),
            "suggestion": info.get("suggestion") or f"Add a project or bullet showing hands-on {skill}.",
            "resource": info.get("resource", ""),
        })
    return out
