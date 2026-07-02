from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

# ==========================================================
# DATABASE ANALYSIS MODEL
# ==========================================================


class AnalysisBase(BaseModel):

    filename: str
    file_path: str

    file_type: str
    file_extension: Optional[str] = None
    file_size: Optional[float] = None

    prediction: str
    confidence: float

    real_probability: Optional[float] = None
    fake_probability: Optional[float] = None

    deepfake_type: Optional[str] = None
    type_confidence: Optional[float] = None

    risk_level: str

    model_name: str
    model_version: str

    device: str

    processing_time: float

    status: str

    face_detected: bool
    face_count: int

    image_width: Optional[int] = None
    image_height: Optional[int] = None

    video_duration: Optional[float] = None

    frames_analyzed: Optional[int] = None
    fake_frames: Optional[int] = None
    real_frames: Optional[int] = None

    verified_result: Optional[str] = None

    remarks: Optional[str] = None


class AnalysisResponse(AnalysisBase):

    id: int

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# ==========================================================
# IMAGE / VIDEO DETECTION API RESPONSE
# ==========================================================


class PredictionSchema(BaseModel):

    label: str

    confidence: float

    riskLevel: str


class ProbabilitySchema(BaseModel):

    real: float

    fake: float


class DeepfakeSchema(BaseModel):

    type: Optional[str] = None

    confidence: Optional[float] = None


class ModelSchema(BaseModel):

    name: str

    version: str

    device: str


class ProcessingSchema(BaseModel):

    time: float


class ImageInformationSchema(BaseModel):

    filename: str

    width: Optional[int] = None

    height: Optional[int] = None

    faceDetected: bool

    faceCount: int


class VideoInformationSchema(BaseModel):

    filename: str

    duration: Optional[float] = None

    framesAnalyzed: Optional[int] = None

    fakeFrames: Optional[int] = None

    realFrames: Optional[int] = None


class ImageDetectionResponse(BaseModel):

    analysisId: int

    prediction: PredictionSchema

    probabilities: ProbabilitySchema

    deepfake: DeepfakeSchema

    model: ModelSchema

    processing: ProcessingSchema

    image: ImageInformationSchema


class VideoDetectionResponse(BaseModel):

    analysisId: int

    prediction: PredictionSchema

    probabilities: ProbabilitySchema

    model: ModelSchema

    processing: ProcessingSchema

    video: VideoInformationSchema


# ==========================================================
# DASHBOARD
# ==========================================================


class DashboardOverviewResponse(BaseModel):

    totalDetection: int

    totalImages: int

    totalVideos: int

    totalFake: int

    totalReal: int

    averageConfidence: float

    averageProcessingTime: float

    latestPrediction: Optional[str]

    latestModel: Optional[str]

    latestConfidence: Optional[float]

    latestVersion: Optional[str] = None

    device: Optional[str] = None

    todayDetection: int = 0

    weekDetection: int = 0

    fakePercentage: float = 0

    realPercentage: float = 0

    imagePercentage: float = 0

    videoPercentage: float = 0