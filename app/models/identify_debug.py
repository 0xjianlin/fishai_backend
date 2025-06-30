from fastapi import APIRouter, UploadFile, File
from PIL import Image
import io
from fish_classifier import classify

router = APIRouter()

@router.post("/identify")
async def identify_fish(image: UploadFile = File(...)):
    contents = await image.read()
    pil_image = Image.open(io.BytesIO(contents)).convert("RGB")
    print("[INFO] Received image:", image.filename)
    print("[INFO] Image size:", pil_image.size)

    results = classify(pil_image)
    print("[INFO] Classification result:", results)
    return results