import httpx
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, HttpUrl

from pdf_diff_analyzer import compare_pdfs

app = FastAPI(title="PDF Diff Analyzer", version="1.0.0")


# ── URL-based comparison ──────────────────────────────────────────────────────

class CompareUrlRequest(BaseModel):
    pdf1_url: HttpUrl
    pdf2_url: HttpUrl


@app.post("/compare/urls", response_class=PlainTextResponse, summary="Compare two PDFs by URL")
async def compare_by_urls(body: CompareUrlRequest) -> str:
    async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
        r1 = await client.get(str(body.pdf1_url))
        r2 = await client.get(str(body.pdf2_url))

    if r1.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Could not fetch pdf1_url: HTTP {r1.status_code}")
    if r2.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Could not fetch pdf2_url: HTTP {r2.status_code}")

    return compare_pdfs(
        r1.content, r2.content,
        label1=str(body.pdf1_url),
        label2=str(body.pdf2_url),
    )


# ── File-upload comparison ────────────────────────────────────────────────────

@app.post("/compare/files", response_class=PlainTextResponse, summary="Compare two uploaded PDF files")
async def compare_by_files(
    pdf1: UploadFile = File(..., description="First PDF"),
    pdf2: UploadFile = File(..., description="Second PDF"),
) -> str:
    pdf1_bytes = await pdf1.read()
    pdf2_bytes = await pdf2.read()
    return compare_pdfs(
        pdf1_bytes, pdf2_bytes,
        label1=pdf1.filename or "pdf1",
        label2=pdf2.filename or "pdf2",
    )


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health", summary="Health check")
async def health():
    return {"status": "ok"}
