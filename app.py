Hugging Face's logo
Hugging Face
Models
Datasets
Spaces
Community
Docs
Enterprise
Pricing


Hugging Face is way more fun with friends and colleagues! 🤗 Join an organization
Spaces:
aykutsen1987
/
tometa-api


like
0

Logs
App
Files
Community
Settings
tometa-api
/
app.py

aykutsen1987's picture
aykutsen1987
Create app.py
1343945
verified
about 2 hours ago
raw

Copy download link
history
blame
edit
delete

926 Bytes
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import os
import shutil
from pdf2docx import Converter

app = FastAPI()

@app.get("/")
def home():
    return {"status": "ToMeta API is running"}

@app.post("/convert/pdf-to-docx")
async def pdf_to_docx(file: UploadFile = File(...)):
    input_path = f"temp_{file.filename}"
    output_path = input_path.replace(".pdf", ".docx")
    
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        cv = Converter(input_path)
        cv.convert(output_path, start=0, end=None)
        cv.close()
        return FileResponse(output_path, filename=f"converted_{file.filename.replace('.pdf', '.docx')}")
    except Exception as e:
        return {"error": str(e)}
    finally:
        # Geçici dosyaları temizleme (isteğe bağlı)
        if os.path.exists(input_path): os.remove(input_path)
