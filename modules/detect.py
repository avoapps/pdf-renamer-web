# ============================================================
# detect.py  | V1.0.1
# ============================================================

import re

def detect_receiver(text):
    text = text.lower().strip()

    patterns = {
        "Cesi": ["cesi"],
        "InoCore": ["inocore", "ino core"],
        "Janniki": ["janniki"]
    }

    for name, keywords in patterns.items():
        for k in keywords:
            if re.search(rf"\b{k}\b", text):
                return name

    return None

# ============================================================
# detect.py | END | V1.0.1
# ============================================================
