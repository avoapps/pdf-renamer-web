# ============================================================
# stamp.py | V1.0.1
# ============================================================




import fitz
import io
import os
from PIL import Image


def insert_stamp(
    pdf_bytes,
    receiver,
    stamp_map,
    date_received,
    year,
    prefix,
    registration_no,
    offset_x,
    offset_y,
    format_date
):

    if not receiver:
        return pdf_bytes

    stamp_path = stamp_map.get(receiver)

    if not stamp_path or not os.path.exists(stamp_path):
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

    x0 = (page_width - target_width) / 2 + offset_x
    y0 = 20 + offset_y

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

    if date_received:
        page.insert_text(
            (x0 + date_x, y1 - date_y),
            format_date(date_received),
            fontsize=14,
            color=(0, 0, 0)
        )

    reg_text = f"{year}-{prefix}-{registration_no}"

    page.insert_text(
        (x0 + reg_x, y1 - reg_y),
        reg_text,
        fontsize=14,
        color=(0, 0, 0)
    )

    output = io.BytesIO()
    doc.save(output)
    doc.close()

    return output.getvalue()

# ============================================================
# stamp.py  | END | V1.0.1
# ============================================================