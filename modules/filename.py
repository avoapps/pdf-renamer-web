# ============================================================
# filename.py  | V1.0.1
# ============================================================


import re

def clean(t):
    t = re.sub(r"[^\w\- ]", "", t)
    t = re.sub(r"\s+", "_", t)
    return t[:50]

def generate_filename(state):
    if not state.get("date_inv_issued"):
        return "⚠️ Missing invoice date"

    date_part = state["date_inv_issued"].strftime("%y%m%d")
    reg = state.get("registration_no", "000000")

    return f"PR {state['year']}-{state['prefix']}-{reg}_{date_part}_{clean(state['company'])}_{clean(state['invoice'])}.pdf"


# ============================================================
# filename.py | END | V1.0.1
# ============================================================
