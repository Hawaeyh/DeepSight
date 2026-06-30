from fastapi import APIRouter, File, UploadFile

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"],
)

@router.post("/image")
async def analyze_image(file: UploadFile = File(...)):
    return {
        "prediction": "Fake",
        "confidence": 98.42,
        "riskLevel": "High",
        "modelVersion": "Mock Binary CNN",
        "processingTime": 0.14,
        "filename": file.filename,
    }