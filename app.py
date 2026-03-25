# =========================================================
# 🚀 VERSION: V16.3.2 FINAL (STABLE)
# =========================================================

import streamlit as st
import pdfplumber
import re
import io
import base64
import os
import fitz
from PIL import Image
from datetime import datetime

st.set_page_config(layout="wide")

# =========================================================
# 🟢 APP VERSION VIEWER
# =========================================================
APP_VERSION = "AvoAPP: V16.3.2"

st.markdown(f"""
<div style="
    position: fixed;
    top: 10px;
    right: 20px;
    background: #111827;
    color: #9ca3af;
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 12px;
    z-index: 9999;
    border: 1px solid #2a2d36;
">
    🚀 {APP_VERSION}
</div>
""", unsafe_allow_html=True)

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
    "151 | forengin cumulative": "151",
    "190 | foreign goods": "190",
    "other": "000"
}

COMPANY_DOC_MAP = {
    "grenke": "120",
}

# =========================================================
# STYLE
# =========================================================
st.markdown("""
<style>
header {visibility:hidden;}
.block-container {padding-top:80px;padding-left:40px;padding-right:40px;}
.preview-box {background:#0e1117;padding:16px;border-radius:12px;border:1px solid #2a2d36;}
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

# =========================================================
# STAMP FUNCTION
# =========================================================
def insert_stamp(pdf_bytes):

    receiver = st.session_state.receiver_company

    if not receiver:
        return pdf_bytes

    stamp_path = STAMP_MAP.get(receiver)

    if not stamp_path or not os.path.exists(stamp_path):
        st.error(f"Missing stamp: {stamp_path}")
        return pdf_bytes

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[0]

    target_width = int(page.rect.width * 0.25)

    if receiver in ["InoCore", "Cesi"]:
        target_width = int(target_width * 1.1)

    with Image.open(stamp_path) as img:
        img = img.copy()

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
    "stamp_offset_y": 0,
    "debug": False
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
        st.text_input("Original filename", st.session_state.original_filename)

pdf_bytes = st.session_state.get("pdf_bytes")

# =========================================================
# AUTO LOAD TEMPLATE (LOCAL + WEB SAFE)
# =========================================================
TEMPLATE_PATH = os.path.join(BASE_DIR, "template.pdf")

if not pdf_bytes or len(pdf_bytes) == 0:
    if os.path.exists(TEMPLATE_PATH):
        with open(TEMPLATE_PATH, "rb") as f:
            pdf_bytes = f.read()
            st.session_state.pdf_bytes = pdf_bytes
            st.session_state.original_filename = "template.pdf"

# =========================================================
# PROCESS PDF
# =========================================================
text = ""

if pdf_bytes:
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for p in pdf.pages:
                text += p.extract_text() or ""
    except Exception as e:
        st.error(f"PDF read error: {e}")

    if not text.strip():
        st.warning("No text detected (scanned PDF?)")

    for line in text.split("\n")[:20]:
        if "d.o.o" in line.lower():
            st.session_state.company = line.strip()
            break

    detected = detect_receiver(text)
    if detected and not st.session_state.receiver_company:
        st.session_state.receiver_company = detected

    comp = st.session_state.company.lower()
    for key, value in COMPANY_DOC_MAP.items():
        if key in comp:
            st.session_state.prefix = value

# =========================================================
# FILENAME MIRROR
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

    if "doc_type_label" not in st.session_state:
        st.session_state.doc_type_label = list(DOCUMENT_TYPES.keys())[0]

    selected_label = st.selectbox(
        "Document Type",
        list(DOCUMENT_TYPES.keys()),
        index=list(DOCUMENT_TYPES.keys()).index(st.session_state.doc_type_label)
    )

    st.session_state.doc_type_label = selected_label
    st.session_state.prefix = DOCUMENT_TYPES[selected_label]

    st.session_state.date_inv_issued = st.date_input("Invoice Issue Date", st.session_state.date_inv_issued)
    st.session_state.date_received_inv = st.date_input("Invoice Received Date", st.session_state.date_received_inv)

    st.session_state.company = st.text_input("Company Name", st.session_state.company)
    st.session_state.invoice = st.text_input("Invoice number", st.session_state.invoice)

    reg_input = st.text_input("Registration No.", st.session_state.registration_no)
    st.session_state.registration_no = re.sub(r"\D","",reg_input).zfill(6)

    receiver_options = ["-- Select --","Janniki","InoCore","Cesi"]

    current = st.session_state.receiver_company

    selected_receiver = st.radio(
        "Receiver",
        receiver_options,
        index=receiver_options.index(current) if current in receiver_options else 0
    )

    st.session_state.receiver_company = None if selected_receiver == "-- Select --" else selected_receiver

# =========================================================
# MOVE BUTTONS + RESET
# =========================================================
st.markdown("---")

if pdf_bytes:
    cols = st.columns([1,1,1,1,1], gap="small")

    with cols[0]:
        if st.button("⬅"):
            st.session_state.stamp_offset_x -= 20

    with cols[1]:
        if st.button("➡"):
            st.session_state.stamp_offset_x += 20

    with cols[2]:
        if st.button("⬆"):
            st.session_state.stamp_offset_y -= 20

    with cols[3]:
        if st.button("⬇"):
            st.session_state.stamp_offset_y += 20

    with cols[4]:
        if st.button("Reset"):
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
# PREVIEW (V16.3.2 - FIXED PDF.js VIEWER)
# =========================================================
import streamlit.components.v1 as components

with col1:
    if active_pdf:
        import base64
        b64 = base64.b64encode(active_pdf).decode()

        pdf_js_html = f"""
        <html>
        <head>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>

            <style>
                body {{
                    margin: 0;
                    background: #0e1117;
                    font-family: Arial;
                    color: white;
                }}

                #controls {{
                    display: flex;
                    gap: 10px;
                    padding: 10px;
                    background: #111827;
                    align-items: center;
                }}

                button {{
                    padding: 6px 12px;
                    border: none;
                    border-radius: 6px;
                    background: #1f2937;
                    color: white;
                    cursor: pointer;
                }}

                button:hover {{
                    background: #374151;
                }}

                #viewer {{
                    height: 720px;
                    overflow: auto;
                    display: flex;
                    justify-content: center;
                }}

                .page-container {{
                    position: relative;
                }}

                canvas {{
                    display: block;
                }}

                /* 🔥 FIXED TEXT LAYER */
                .textLayer {{
                    position: absolute;
                    left: 0;
                    top: 0;
                    right: 0;
                    bottom: 0;
                    overflow: hidden;
                    line-height: 1;
                    transform-origin: 0 0;
                }}

                .textLayer span {{
                    position: absolute;
                    white-space: pre;
                    transform-origin: 0 0;
                    color: transparent;
                }}
            </style>
        </head>

        <body>

        <div id="controls">
            <button onclick="prevPage()">⬅</button>
            <span id="page-info">Page 1</span>
            <button onclick="nextPage()">➡</button>
            <button onclick="zoomOut()">-</button>
            <button onclick="zoomIn()">+</button>
            <input type="range" min="0.5" max="3" step="0.1" value="1.5"
                   onchange="setZoom(this.value)">
        </div>

        <div id="viewer">
            <div class="page-container" id="page-container">
                <canvas id="pdf-canvas"></canvas>
                <div id="text-layer" class="textLayer"></div>
            </div>
        </div>

        <script>
            pdfjsLib.GlobalWorkerOptions.workerSrc =
              "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";

            const pdfData = atob("{b64}");

            let pdfDoc = null;
            let pageNum = 1;
            let scale = 1.5;

            const canvas = document.getElementById("pdf-canvas");
            const ctx = canvas.getContext("2d");
            const textLayerDiv = document.getElementById("text-layer");
            const container = document.getElementById("page-container");

            pdfjsLib.getDocument({{data: pdfData}}).promise.then(pdf => {{
                pdfDoc = pdf;
                renderPage(pageNum);
            }});

            function renderPage(num) {{
                pdfDoc.getPage(num).then(page => {{

                    // ✅ FIX: removed dontFlip
                    const viewport = page.getViewport({{
                        scale: scale
                    }});

                    canvas.width = viewport.width;
                    canvas.height = viewport.height;

                    container.style.width = viewport.width + "px";
                    container.style.height = viewport.height + "px";

                    textLayerDiv.innerHTML = "";
                    textLayerDiv.style.width = viewport.width + "px";
                    textLayerDiv.style.height = viewport.height + "px";

                    // Render canvas first
                    page.render({{
                        canvasContext: ctx,
                        viewport: viewport
                    }}).promise.then(() => {{

                        // Render text layer AFTER canvas
                        page.getTextContent().then(textContent => {{
                            pdfjsLib.renderTextLayer({{
                                textContent: textContent,
                                container: textLayerDiv,
                                viewport: viewport,
                                textDivs: []
                            }});
                        }});

                    }});

                    document.getElementById("page-info").innerText =
                        "Page " + num + " / " + pdfDoc.numPages;
                }});
            }}

            function prevPage() {{
                if (pageNum <= 1) return;
                pageNum--;
                renderPage(pageNum);
            }}

            function nextPage() {{
                if (pageNum >= pdfDoc.numPages) return;
                pageNum++;
                renderPage(pageNum);
            }}

            function zoomIn() {{
                scale += 0.2;
                renderPage(pageNum);
            }}

            function zoomOut() {{
                scale = Math.max(0.5, scale - 0.2);
                renderPage(pageNum);
            }}

            function setZoom(val) {{
                scale = parseFloat(val);
                renderPage(pageNum);
            }}
        </script>

        </body>
        </html>
        """

        components.html(pdf_js_html, height=820)

# =========================================================
# DEBUG PANEL
# =========================================================
with st.expander("🔧 Debug (for learning phase)"):
    st.write("Company:", st.session_state.company)
    st.write("Receiver:", st.session_state.receiver_company)
    st.write("Prefix:", st.session_state.prefix)

# =========================================================
# 🟢 VERSION END: V16.3.2 FINAL
# =========================================================