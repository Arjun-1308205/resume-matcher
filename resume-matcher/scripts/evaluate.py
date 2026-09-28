"""Compare TF-IDF vs hybrid scoring against your own labels.

Fill data/labeled_pairs.csv with rows: resume_file,jd_file,human_score (0..1),
put the files in data/, then run:  python scripts/evaluate.py
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd

from core.scoring import match, tfidf_similarity

DATA = Path(__file__).resolve().parent.parent / "data"
df = pd.read_csv(DATA / "labeled_pairs.csv")

rows = []
for r in df.itertuples():
    resume = (DATA / r.resume_file).read_text()
    jd = (DATA / r.jd_file).read_text()
    rows.append({"human": r.human_score, "tfidf_only": tfidf_similarity(resume, jd), "hybrid": match(resume, jd).overall})

res = pd.DataFrame(rows)
print(res.round(3))
if len(res) >= 3:
    print("\nSpearman correlation with human scores:")
    print(res.corr(method="spearman")["human"].drop("human").round(3))
else:
    print("\nAdd at least 3 labeled pairs (30-50 is better) to get correlations.")
