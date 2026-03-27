# =========================================================
# 🚀 VERSION: V17.0.1 Learning
# =========================================================
import streamlit as st
import re
import os
from datetime import datetime

from modules.detect import detect_receiver
from modules.filename import generate_filename
from modules.stamp import insert_stamp
from modules.pdf import extract_text_from_pdf, detect_company_from_text

st.set_page_config(layout="wide")


# =========================================================
# 🟢 APP VERSION VIEWER
# =========================================================
APP_VERSION = "AvoAPP: V17.0.1"

st.markdown(f"""
<div style="
    position: fixed;
    top: 10px;
    left: 20px;
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
# PATH
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
# HEAD 0
# =========================================================

st.markdown("""
<div style="
position:fixed;
top:0;
left:0;
width:100%;
height:90px;
background:#111827;
z-index:9990;
">
</div>
""", unsafe_allow_html=True)




# =========================================================
# HEAD 1
# =========================================================
import base64

logo_path = os.path.join(BASE_DIR, "logo_avoapps.png")

if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <div style="
        position: fixed;
        top: 0px;
        right: 0px;
        width: 150px;
        z-index: 9996;       
    ">
        <img src="data:image/png;base64,{logo_base64}" 
             style="height:200px; display:block;">
    </div>
    """, unsafe_allow_html=True)

else:
    st.write("Logo not found:", logo_path)



# =========================================================
# HEAD 2
# =========================================================
HEAD_2 = "Document Manager APP"

st.markdown(f"""
<div style="
    position: fixed;
    top: 0px;
    left: 600px;
    width:100%
    color: #9ca3af;
    font-size: 48px;
    border: 0px solid #2a2d36;
    background: transparent;  /* 🔑 KLJUČNO: NI transparent */
    z-index:9998;        /* 🔑 NAD vsem */
    display:flex;
    align-items:center;
    justify-content:space-between;
    padding:0 30px;
    border-bottom:0px solid #2a2d36;
">
    🗄️📄 {HEAD_2}
</div>
""", unsafe_allow_html=True)



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
def format_date(d):
    return d.strftime("%d.%m.%Y") if d else ""



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
}

for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# =========================================================
# UPLOAD
# =========================================================
col_upload, col_download = st.columns([0.2,0.5])

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
# TEMPLATE
# =========================================================
TEMPLATE_PATH = os.path.join(BASE_DIR, "template.pdf")

if not pdf_bytes:
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
    text, error = extract_text_from_pdf(pdf_bytes)

    if error:
        st.error(f"PDF read error: {error}")

    if not text.strip():
        st.warning("No text detected (scanned PDF?)")

    detected_company = detect_company_from_text(text)
    if detected_company:
        st.session_state.company = detected_company

    detected = detect_receiver(text)
    if detected and not st.session_state.receiver_company:
        st.session_state.receiver_company = detected

    comp = st.session_state.company.lower()
    for key, value in COMPANY_DOC_MAP.items():
        if key in comp:
            st.session_state.prefix = value

# =========================================================
# FILENAME
# =========================================================
generated_filename = generate_filename(st.session_state)

st.markdown(f"""
<div style="padding:12px;background:#0f172a;border-radius:10px;color:white;text-align:center;">
📄 {generated_filename}
</div>
""", unsafe_allow_html=True)

# =========================================================
# UI
# =========================================================



# MAIN LAYOUT
left, right = st.columns([1, 2])


# =========================================================
# LEFT PANEL (ALL CONTROLS)
# =========================================================

with left:
    colA, colB = st.columns(2)

    with colA:
        # -----------------------------------------------------
        # DOCUMENT TYPE
        # -----------------------------------------------------
        if "doc_type_label" not in st.session_state:
            st.session_state.doc_type_label = list(DOCUMENT_TYPES.keys())[0]

        selected_label = st.selectbox(
            "Document Type",
            list(DOCUMENT_TYPES.keys()),
            index=list(DOCUMENT_TYPES.keys()).index(st.session_state.doc_type_label)
        )

        st.session_state.doc_type_label = selected_label
        st.session_state.prefix = DOCUMENT_TYPES[selected_label]

        # -----------------------------------------------------
        # DATES
        # -----------------------------------------------------
        st.session_state.date_inv_issued = st.date_input(
            "Invoice Issue Date",
            value=st.session_state.date_inv_issued,
            format="DD.MM.YYYY"
        )

        st.session_state.date_received_inv = st.date_input(
            "Invoice Received Date",
            value=st.session_state.date_received_inv,
            format="DD.MM.YYYY"
        )

    with colB: 
        # -----------------------------------------------------
        # TEXT FIELDS
        # -----------------------------------------------------
        st.session_state.company = st.text_input(
            "Company Name",
            st.session_state.company
        )

        st.session_state.invoice = st.text_input(
            "Invoice number",
            st.session_state.invoice
        )

        # -----------------------------------------------------
        # REGISTRATION NUMBER
        # -----------------------------------------------------
        reg_input = st.text_input(
            "Registration No.",
            st.session_state.registration_no
        )

        st.session_state.registration_no = re.sub(r"\D", "", reg_input).zfill(6)


    # =========================================================
    # LEFT BOTTOM PANEL (ALL CONTROLS)
    # =========================================================
    bottom_left, bottom_right = st.columns([1, 2])

    with bottom_left:

            # -----------------------------------------------------
            # RECEIVER
            # -----------------------------------------------------
            receiver_options = ["-- Select --","Janniki","InoCore","Cesi"]

            if "receiver_company" not in st.session_state:
                st.session_state.receiver_company = "-- Select --"

            current = st.session_state.receiver_company

            selected_receiver = st.radio(
                "Receiver",
                receiver_options,
                index=receiver_options.index(current) if current in receiver_options else 0,
                key="receiver_company"
            )

            receiver = None if selected_receiver == "-- Select --" else selected_receiver

    with bottom_right:
            # -----------------------------------------------------
            # MOVE (BETTER UI)
            # -----------------------------------------------------
            if pdf_bytes:

                st.markdown("### 🎯 Move Stamp")

                col_empty1, col_up, col_empty2 = st.columns([1,1,1])
                with col_up:
                    if st.button("⬆", use_container_width=True):
                        st.session_state.stamp_offset_y -= 20

                col_left, col_reset, col_right = st.columns([1,1,1])

                with col_left:
                    if st.button("⬅", use_container_width=True):
                        st.session_state.stamp_offset_x -= 20

                with col_reset:
                    if st.button("Reset", use_container_width=True):
                        st.session_state.stamp_offset_x = 0
                        st.session_state.stamp_offset_y = 0

                with col_right:
                    if st.button("➡", use_container_width=True):
                        st.session_state.stamp_offset_x += 20

                col_empty3, col_down, col_empty4 = st.columns([1,1,1])
                with col_down:
                    if st.button("⬇", use_container_width=True):
                        st.session_state.stamp_offset_y += 20


# =========================================================
# RIGHT PANEL (RESERVED FOR PREVIEW)
# =========================================================
with right:
    pass  # preview block je spodaj (že si ga popravil)

# =========================================================
# PDF OUTPUT
# =========================================================
from services.processor import process_pdf

active_pdf = None

if pdf_bytes:
    active_pdf, error = process_pdf(
        pdf_bytes,
        st.session_state,
        STAMP_MAP,
        format_date
    )

    if error:
        st.error(error)

# =========================================================
# DOWNLOAD
# =========================================================
with left:

    if active_pdf:
        st.markdown("### 💾 Export")

        st.download_button(
            "⬇️ Download PDF",
            active_pdf,
            file_name=generated_filename,
            use_container_width=True
        )

    # -----------------------------------------------------
    # DEBUG
    # -----------------------------------------------------
    
    st.markdown("### 💾 Debug")

    with st.expander("🔧 Debug"):
        st.write("Company:", st.session_state.company)
        st.write("Receiver:", st.session_state.receiver_company)
        st.write("Prefix:", st.session_state.prefix)


# =========================================================
# PREVIEW (V16.3.2 - FIXED PDF.js VIEWER)
# =========================================================
import streamlit.components.v1 as components

with right:

    # -----------------------------------------------------
    # STATUS
    # -----------------------------------------------------
    if not st.session_state.date_inv_issued:
        st.markdown("""
        <div style="
            display:inline-block;
            background:#1e293b;
            color:#facc15;
            padding:6px 12px;
            border-radius:8px;
            font-size:13px;
            margin-bottom:10px;
        ">
            ⚠ Missing invoice date
        </div>
        """, unsafe_allow_html=True)

    # -----------------------------------------------------
    # PREVIEW 
    # -----------------------------------------------------
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
                    height: 1000px;
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

                    page.render({{
                        canvasContext: ctx,
                        viewport: viewport
                    }}).promise.then(() => {{

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
# 🟢 VERSION | END | : V17.0.1
# =========================================================