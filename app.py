from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import shutil
import uuid

from pdf2docx import Converter
from PIL import Image
from docx import Document
from pdfminer.high_level import extract_text

app = FastAPI()

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.get("/")
def home():
    return {"status": "ToMeta API is running"}

# =========================
# PDF → DOCX
# =========================
@app.post("/convert/pdf-to-docx")
async def pdf_to_docx(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "PDF dosyası gerekli")

    uid = str(uuid.uuid4())
    input_path = f"{TEMP_DIR}/{uid}.pdf"
    output_path = f"{TEMP_DIR}/{uid}.docx"

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        cv = Converter(input_path)
        cv.convert(output_path)
        cv.close()
        return FileResponse(output_path, filename="converted.docx")
    finally:
        cleanup(input_path)

# =========================
# PDF → TXT
# =========================
@app.post("/convert/pdf-to-txt")
async def pdf_to_txt(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "PDF dosyası gerekli")

    uid = str(uuid.uuid4())
    input_path = f"{TEMP_DIR}/{uid}.pdf"
    output_path = f"{TEMP_DIR}/{uid}.txt"

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        text = extract_text(input_path)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        return FileResponse(output_path, filename="converted.txt")
    finally:
        cleanup(input_path)

# =========================
# DOCX → TXT
# =========================
@app.post("/convert/docx-to-txt")
async def docx_to_txt(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(400, "DOCX dosyası gerekli")

    uid = str(uuid.uuid4())
    input_path = f"{TEMP_DIR}/{uid}.docx"
    output_path = f"{TEMP_DIR}/{uid}.txt"

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        doc = Document(input_path)
        with open(output_path, "w", encoding="utf-8") as f:
            for p in doc.paragraphs:
                f.write(p.text + "\n")
        return FileResponse(output_path, filename="converted.txt")
    finally:
        cleanup(input_path)

# =========================
# IMAGE CONVERT (JPEG ↔ PNG)
# =========================
@app.post("/convert/image")
async def image_convert(
    file: UploadFile = File(...),
    target_format: str = "png"
):
    uid = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1].lower()
    input_path = f"{TEMP_DIR}/{uid}{ext}"
    output_path = f"{TEMP_DIR}/{uid}.{target_format}"

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        img = Image.open(input_path)
        img.save(output_path)
        return FileResponse(output_path, filename=f"converted.{target_format}")
    finally:
        cleanup(input_path)

# =========================
# Helper
# =========================
def cleanup(path):
    if os.path.exists(path):
        os.remove(path)
