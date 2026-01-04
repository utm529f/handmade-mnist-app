from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class SampleCreate(BaseModel):
    digit: int = Field(..., ge=0, le=9)
    imageData: List[float] = Field(..., min_length=784, max_length=784)

class SampleResponse(BaseModel):
    id: int
    message: str

class DataStatus(BaseModel):
    valid: bool
    total: int
    perDigit: List[int]
    missingDigits: List[int]

class SampleDigitResponse(BaseModel):
    id: int
    digit: int
    imageData: List[float]

class TrainRequest(BaseModel):
    epochs: int = 20
    batchSize: int = 16

class TrainResponse(BaseModel):
    status: str
    taskId: str

class TrainStatusResponse(BaseModel):
    status: str
    progress: int
    epoch: int
    totalEpochs: int
    accuracy: float
    loss: float

class QuestionRequest(BaseModel):
    mode: str = "mixed"

class QuestionResponse(BaseModel):
    questionId: str
    num1: int
    num2: int
    num1Image: List[float]
    num2Image: List[float]
    operator: str
    answer: int
    is2Digit: bool

class AnswerRequest(BaseModel):
    questionId: str
    onesImageData: List[float]
    tensImageData: Optional[List[float]] = None

class AnswerResponse(BaseModel):
    recognizedAnswer: int
    correct: bool
    confidence: float
    correctAnswer: int

class ModelStatus(BaseModel):
    cnn: dict
    vae: dict
