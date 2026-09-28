# AI Resume Analyzer & Job Matcher

Upload a resume, paste a job description, and get a hybrid match score, matched and missing skills, and suggestions for closing the gaps.

## Setup (VS Code)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate     Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

Run tests: `pytest -q`. Evaluate against your labels: `python scripts/evaluate.py`.

If you want a light install, delete `sentence-transformers` from `requirements.txt`; the app still works with TF-IDF and the embeddings toggle will show a message.

## Where things live

| Path | Purpose |
|---|---|
| `data/skills.csv` | Skill taxonomy: `skill,category,aliases` (aliases separated by `\|`). Add rows to teach the app new skills. |
| `data/recommendations.csv` | Suggestion and resource shown for each missing skill. |
| `data/sample_*.txt` | Sample resume and JD (button in the sidebar loads them). |
| `data/labeled_pairs.csv` | Your hand-labelled pairs for `scripts/evaluate.py`. |
| `core/` | parser, skills extraction, scoring, recommendations, privacy. |
| `app/streamlit_app.py` | Dashboard. |
| `tests/` | pytest suite. |

## How scoring works

`overall = 0.35 * text similarity + 0.50 * skill coverage + 0.15 * experience fit` (weights in `core/scoring.py`).

- Text similarity: TF-IDF cosine, or `all-MiniLM-L6-v2` embeddings when toggled on.
- Skill coverage: share of the JD's skills found in the resume.
- Experience fit: years and degree level versus what the JD asks for.

## Fairness note

Emails, phone numbers, links and gendered markers are stripped before scoring. Names are not removed automatically, and the scores are a screening aid, not a hiring decision.

## Deploy

- Easiest: push to GitHub, then deploy on Streamlit Community Cloud with main file `app/streamlit_app.py`.
- Docker: `docker build -t resume-matcher . && docker run -p 8501:8501 resume-matcher`.
