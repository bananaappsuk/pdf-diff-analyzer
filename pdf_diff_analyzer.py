import base64
import fitz  # PyMuPDF
from openai import OpenAI


def pdf_bytes_to_base64_images(pdf_bytes: bytes) -> list[str]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []
    for page in doc:
        pix = page.get_pixmap(dpi=150)
        images.append(base64.b64encode(pix.tobytes("png")).decode())
    return images


def compare_pdfs(pdf1_bytes: bytes, pdf2_bytes: bytes, label1: str = "Document 1", label2: str = "Document 2") -> str:
    images1 = pdf_bytes_to_base64_images(pdf1_bytes)
    images2 = pdf_bytes_to_base64_images(pdf2_bytes)

    content = [{"type": "text", "text": f"DOCUMENT 1: {label1}"}]
    for img in images1:
        content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img}"}})

    content.append({"type": "text", "text": f"DOCUMENT 2: {label2}"})
    for img in images2:
        content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img}"}})

    content.append({
        "type": "text",
        "text": (
            "Compare these two documents thoroughly and produce a structured plain-text report covering:\n"
            "1. High-level summary of what changed.\n"
            "2. Section-by-section breakdown of additions, deletions, and modifications.\n"
            "3. Any notable differences in numbers, dates, names, dimensions, or key terms.\n"
            "Write the report in plain text."
        ),
    })

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[{"role": "user", "content": content}],
    )
    return response.choices[0].message.content
