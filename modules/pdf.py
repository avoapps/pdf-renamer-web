# ============================================================
# pdf.py | V1.0.1
# ============================================================

import pdfplumber
import io


def extract_text_from_pdf(pdf_bytes):
    text = ""

    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    except Exception as e:
        return "", str(e)

    return text, None


def detect_company_from_text(text):
    for line in text.split("\n")[:20]:
        if "d.o.o" in line.lower():
            return line.strip()

    return None

# ============================================================
# pdf.py  | END | V1.0.1
# ============================================================