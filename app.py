# =========================================================
# 🚀 VERSION: V16.1.3 FINAL (PDF.js + FALLBACK PREVIEW)
# =========================================================

import streamlit as st
import pdfplumber
import re
import io
import os
import fitz
import base64
from PIL import Image
from datetime import datetime

st.set_page_config(layout="wide")

# =========================================================
# PATH (WEB SAFE)
# =========================================================
BASE_DIR = os.path.dirname(__file__)

STAMP_MAP = {
    "Janniki": os.path.join(BASE_DIR, "Stamp_Janniki_recieved.png"),
    "InoCore": os.path.join(BASE_DIR, "Stamp_InoCore_recieved.png"),
    "Cesi": os.path.join(BASE_DIR, "Stamp_Cesi_recieved.png")
}

DOCUMENT_TYPES = {
    "100 | domestic goods": "100",
    "120 | domestic expense": "120",
    "122 | foreign expense": "122",
    "123 | card": "123",
    "150 | domestic cumulative": "150",
    "151 | foreign cumulative": "151",
    "190 | foreign goods": "190",
    "other": "000"
}

# =========================================================
# STYLE
# =========================================================
st.markdown("""
<style>
header {visibility:hidden;}
.block-container {padding-top:80px;padding-left:40px;padding-right:40px;}
.preview-box {background:#0e1117;padding:16px;border-radius:12px;border:1px solid #2a2d36; position:relative;}
#text-layer {pointer-events:auto;}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HELPERS
# =========================================================
def clean(t):
    return re.sub(r"[^\w\- ]", "", t).strip()

def format_date(d):
    return d.strftime("%d.%m.%Y") if d else ""

def generate_filename():
    if not st.session_state.get("date_inv_issued"):
        return "⚠️ Missing invoice date"

    date_part = st.session_state.date_inv_issued.strftime("%y%m%d")
    reg = st.session_state.get("registration_no", "000000")

    return f"PR {st.session_state.year}-{st.session_state.prefix}-{reg}_{date_part}_{clean(st.session_state.company)}_{clean(st.session_state.invoice)}.pdf"

def detect_receiver(text):
    normalized = re.sub(r"[^a-z]", "", text.lower())
    if "cesi" in normalized:
        return "Cesi"
    if "inocore" in normalized:
        return "InoCore"
    if "janniki" in normalized:
        return "Janniki"
    return None

def render_pdf_preview(pdf_bytes):
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_bytes = pix.tobytes("png")
        doc.close()
        return img_bytes
    except:
        return None

# =========================================================
# STAMP FUNCTION
# =========================================================
def insert_stamp(pdf_bytes):

    receiver = st.session_state.receiver_company
    if not receiver:
        return pdf_bytes

    stamp_path = STAMP_MAP.get(receiver)
    if not stamp_path or not os.path.exists(stamp_path):
        return pdf_bytes

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[0]

    target_width = int(page.rect.width * 0.25)
    if receiver in ["InoCore", "Cesi"]:
        target_width = int(target_width * 1.1)

    img = Image.open(stamp_path)
    ratio = target_width / img.width
    target_height = int(img.height * ratio)
    img = img.resize((target_width, target_height), Image.LANCZOS)

    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    page_width = page.rect.width

    x0 = (page_width - target_width) / 2 + st.session_state.stamp_offset_x
    y0 = 20 + st.session_state.stamp_offset_y

    x0 = max(0, min(x0, page_width - target_width))
    y0 = max(0, y0)

    y1 = y0 + target_height

    rect = fitz.Rect(x0, y0, x0 + target_width, y1)
    page.insert_image(rect, stream=img_bytes.getvalue())

    if receiver in ["Cesi", "InoCore"]:
        date_x = int(target_width * 0.35)
        date_y = int(target_height * 0.55)
        reg_x = int(target_width * 0.30)
        reg_y = int(target_height * 0.35)
    else:
        date_x, date_y = 65, 60
        reg_x, reg_y = 55, 40

    if st.session_state.date_received_inv:
        page.insert_text(
            (x0 + date_x, y1 - date_y),
            format_date(st.session_state.date_received_inv),
            fontsize=14,
            color=(0,0,0)
        )

    reg_text = f"{st.session_state.year}-{st.session_state.prefix}-{st.session_state.registration_no}"

    page.insert_text(
        (x0 + reg_x, y1 - reg_y),
        reg_text,
        fontsize=14,
        color=(0,0,0)
    )

    output = io.BytesIO()
    doc.save(output)
    doc.close()

    return output.getvalue()

# =========================================================
# SESSION STATE
# =========================================================
defaults = {
    "prefix": "100",
    "year": datetime.now().strftime("%y"),
    "company": "Company name",
    "invoice": "INV-XXX",
    "date_inv_issued": None,
    "date_received_inv": None,
    "original_filename": "",
    "registration_no": "000000",
    "receiver_company": None,
    "pdf_bytes": None,
    "stamp_offset_x": 0,
    "stamp_offset_y": 0
}

for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# =========================================================
# UPLOAD
# =========================================================
col_upload, col_download = st.columns([2,1])

with col_upload:
    uploaded = st.file_uploader("Upload PDF", type="pdf")

    if uploaded and st.session_state.original_filename != uploaded.name:
        st.session_state.pdf_bytes = uploaded.read()
        st.session_state.original_filename = uploaded.name
        st.session_state.stamp_offset_x = 0
        st.session_state.stamp_offset_y = 0

    if st.session_state.original_filename:
        st.text_input("Original filename", st.session_state.original_filename, disabled=True)

pdf_bytes = st.session_state.get("pdf_bytes")

# =========================================================
# PROCESS PDF
# =========================================================
text = ""
if pdf_bytes:
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for p in pdf.pages:
                text += p.extract_text() or ""
    except:
        pass

    detected = detect_receiver(text)
    if detected and not st.session_state.receiver_company:
        st.session_state.receiver_company = detected

# =========================================================
# FILENAME
# =========================================================
final_name = generate_filename()

st.markdown(f"""
<div style="padding:12px;background:#0f172a;border-radius:10px;color:white;text-align:center;">
📄 {final_name}
</div>
""", unsafe_allow_html=True)

# =========================================================
# UI
# =========================================================
col1, col2 = st.columns([1.6,1])

with col2:
    selected_label = st.selectbox("Document Type", list(DOCUMENT_TYPES.keys()))
    st.session_state.prefix = DOCUMENT_TYPES[selected_label]

    st.session_state.date_inv_issued = st.date_input("Invoice Issue Date", st.session_state.date_inv_issued)
    st.session_state.date_received_inv = st.date_input("Invoice Received Date", st.session_state.date_received_inv)

    st.session_state.company = st.text_input("Company Name", st.session_state.company)
    st.session_state.invoice = st.text_input("Invoice number", st.session_state.invoice)

    reg_input = st.text_input("Registration No.", st.session_state.registration_no)
    st.session_state.registration_no = re.sub(r"\D","",reg_input).zfill(6)

    receiver_options = ["Janniki","InoCore","Cesi"]
    current = st.session_state.receiver_company

    st.session_state.receiver_company = st.radio(
        "Receiver",
        receiver_options,
        index=receiver_options.index(current) if current in receiver_options else 0
    )

# =========================================================
# MOVE BUTTONS + RESET
# =========================================================
st.markdown("---")

if pdf_bytes:
    cols = st.columns([1,1,1,1,1], gap="small")

    if cols[0].button("⬅"):
        st.session_state.stamp_offset_x -= 20
    if cols[1].button("➡"):
        st.session_state.stamp_offset_x += 20
    if cols[2].button("⬆"):
        st.session_state.stamp_offset_y -= 20
    if cols[3].button("⬇"):
        st.session_state.stamp_offset_y += 20
    if cols[4].button("Reset"):
        st.session_state.stamp_offset_x = 0
        st.session_state.stamp_offset_y = 0

# =========================================================
# ACTIVE PDF
# =========================================================
active_pdf = insert_stamp(pdf_bytes) if pdf_bytes else None

# =========================================================
# DOWNLOAD
# =========================================================
with col_download:
    if active_pdf:
        st.download_button("⬇️ Download PDF", active_pdf, file_name=final_name)

# =========================================================
# PREVIEW (PDF.js + FALLBACK)
# =========================================================
with col1:
    if active_pdf:

        pdf_base64 = base64.b64encode(active_pdf).decode()

        st.markdown(f"""
        <div class="preview-box">
            <canvas id="pdf-canvas"></canvas>
            <div id="text-layer"></div>
        </div>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>

        <script>
        const pdfData = atob("{pdf_base64}");
        const loadingTask = pdfjsLib.getDocument({{data: pdfData}});

        loadingTask.promise.then(function(pdf) {{
            pdf.getPage(1).then(function(page) {{

                const scale = 1.5;
                const viewport = page.getViewport({{ scale: scale }});

                const canvas = document.getElementById('pdf-canvas');
                const context = canvas.getContext('2d');

                canvas.height = viewport.height;
                canvas.width = viewport.width;

                page.render({{
                    canvasContext: context,
                    viewport: viewport
                }});

                page.getTextContent().then(function(textContent) {{
                    pdfjsLib.renderTextLayer({{
                        textContent: textContent,
                        container: document.getElementById('text-layer'),
                        viewport: viewport,
                        textDivs: []
                    }});
                }});
            }});
        }}).catch(function(error) {{
            console.log("PDF.js failed");
        }});
        </script>
        """, unsafe_allow_html=True)

        # FALLBACK
        preview_img = render_pdf_preview(active_pdf)
        if preview_img:
            st.image(preview_img, use_container_width=True)

# =========================================================
# 🟢 VERSION END: V16.1.3 FINAL
# =========================================================