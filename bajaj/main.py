from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List
import pytesseract
import cv2
import numpy as np
from PIL import Image
import io
import re

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = FastAPI()

@app.post("/get-lab-tests")
async def get_lab_tests(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        image = np.array(image)

        # Preprocess image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray)

        lab_tests = extract_lab_tests(text)

        return JSONResponse(content={
            "is_success": True,
            "data": lab_tests
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "is_success": False,
            "error": str(e)
        })

def extract_lab_tests(text: str) -> List[dict]:
    lines = text.splitlines()
    results = []
    for line in lines:
        # Simple regex pattern: Name, Value, Unit, Range
        match = re.search(r"([A-Za-z0-9\s()./%-]+?)\s+([0-9.]+)\s*([a-zA-Z%/]+)?\s+(\d+\.?\d*)\s*[-toTO]+\s*(\d+\.?\d*)", line)
        if match:
            test_name = match.group(1).strip()
            test_value = float(match.group(2))
            test_unit = match.group(3) or ""
            ref_low = float(match.group(4))
            ref_high = float(match.group(5))
            out_of_range = not (ref_low <= test_value <= ref_high)

            results.append({
                "test_name": test_name,
                "test_value": str(test_value),
                "test_unit": test_unit,
                "bio_reference_range": f"{ref_low}-{ref_high}",
                "lab_test_out_of_range": out_of_range
            })
    return results