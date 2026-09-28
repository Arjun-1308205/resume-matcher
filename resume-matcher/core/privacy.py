"""Basic anonymisation so scoring is not influenced by personal identifiers."""
import re

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE = re.compile(r"(\+?\d[\d\s().-]{8,}\d)")
URL = re.compile(r"(https?://\S+|www\.\S+|linkedin\.com/\S+|github\.com/\S+)", re.I)
GENDER_WORDS = re.compile(r"\b(male|female|he/him|she/her|they/them|mr\.?|mrs\.?|ms\.?)\b", re.I)


def anonymise(text: str) -> str:
    """Remove contact details and gendered markers. Names are not removed
    automatically; see README for the limitation."""
    for pattern in (EMAIL, PHONE, URL, GENDER_WORDS):
        text = pattern.sub(" ", text)
    return re.sub(r"[ \t]+", " ", text)
