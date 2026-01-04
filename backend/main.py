from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import database
import schemas
import crud
import train as train_module
from pathlib import Path

app = FastAPI(title="Handmade MNIST API")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    database.init_db()

@app.get("/")
async def root():
    return {"message": "Handmade MNIST API"}

# データ収集API
@app.post("/api/samples", response_model=schemas.SampleResponse)
async def create_sample(sample: schemas.SampleCreate):
    sample_id = crud.save_sample(sample.digit, sample.imageData)
    return schemas.SampleResponse(id=sample_id, message="Sample saved successfully")

@app.get("/api/samples/status", response_model=schemas.DataStatus)
async def get_samples_status():
    return crud.get_data_status()

@app.get("/api/samples/digit/{digit}", response_model=schemas.SampleDigitResponse)
async def get_random_sample(digit: int):
    if digit < 0 or digit > 9:
        raise HTTPException(status_code=400, detail="Digit must be 0-9")
    sample = crud.get_random_sample_by_digit(digit)
    if not sample:
        raise HTTPException(status_code=404, detail=f"No samples found for digit {digit}")
    return sample

@app.delete("/api/data/reset")
async def reset_all_data():
    """Delete all samples, models, and game history"""
    try:
        crud.reset_all_data()
        return {"message": "All data reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# モデル学習API
@app.post("/api/train/cnn", response_model=schemas.TrainResponse)
async def start_cnn_training(request: schemas.TrainRequest):
    task_id = train_module.start_cnn_training_async(request.epochs, request.batchSize)
    return schemas.TrainResponse(status="training_started", taskId=task_id)

@app.get("/api/train/cnn/status/{task_id}", response_model=schemas.TrainStatusResponse)
async def get_cnn_training_status(task_id: str):
    status = train_module.get_training_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    return status

@app.get("/api/models/status", response_model=schemas.ModelStatus)
async def get_models_status():
    return crud.get_models_status()

# ゲームAPI
@app.post("/api/game/question", response_model=schemas.QuestionResponse)
async def create_question(request: schemas.QuestionRequest):
    question = crud.generate_question(request.mode)
    return question

@app.post("/api/game/answer", response_model=schemas.AnswerResponse)
async def submit_answer(request: schemas.AnswerRequest):
    result = crud.check_answer(request)
    return result

@app.get("/api/game/history")
async def get_game_history():
    history = crud.get_game_history()
    return {"history": history}
