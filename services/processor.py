# ============================================================
# processor.py | V1.0.1
# ============================================================


from modules.pdf import extract_text_from_pdf, detect_company_from_text
from modules.detect import detect_receiver
from modules.stamp import insert_stamp

def process_pdf(pdf_bytes, session, stamp_map, format_date):

    text, error = extract_text_from_pdf(pdf_bytes)

    if error:
        return None, error

    # COMPANY
    detected_company = detect_company_from_text(text)
    if detected_company:
        session.company = detected_company

    # RECEIVER
    detected = detect_receiver(text)
    if detected and not session.receiver_company:
        session.receiver_company = detected

    # STAMP
    output_pdf = insert_stamp(
        pdf_bytes,
        session.receiver_company,
        stamp_map,
        session.date_received_inv,
        session.year,
        session.prefix,
        session.registration_no,
        session.stamp_offset_x,
        session.stamp_offset_y,
        format_date
    )

    return output_pdf, None

# ============================================================
# processor.py  | END | V1.0.1
# ============================================================