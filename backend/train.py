import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import sqlite3
import uuid
import threading
from typing import Callable, Dict, List
from pathlib import Path
from database import DB_PATH
from models import DigitCNN, DigitVAE
import io

# 学習タスク管理
training_tasks = {}

class SamplesDataset(Dataset):
    """手書き数字データセット"""
    def __init__(self, samples):
        self.samples = samples

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        digit, image_data = self.samples[idx]
        # 28x28に reshape
        image = np.frombuffer(image_data, dtype=np.float32).reshape(1, 28, 28)
        return torch.FloatTensor(image), digit

def load_all_samples():
    """全サンプルをロード"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT digit, image_data FROM samples")
    samples = cursor.fetchall()
    conn.close()
    return samples

def train_cnn_model(epochs: int, batch_size: int, progress_callback: Callable):
    """CNNモデルを学習"""
    # デバイス設定
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # データ読み込み
    samples = load_all_samples()
    dataset = SamplesDataset(samples)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # モデル初期化
    model = DigitCNN().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # 学習ループ
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for images, labels in dataloader:
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

        epoch_loss = running_loss / len(dataloader)
        epoch_acc = correct / total

        # 進捗コールバック
        progress_callback({
            "status": "training",
            "progress": int((epoch + 1) / epochs * 100),
            "epoch": epoch + 1,
            "totalEpochs": epochs,
            "accuracy": epoch_acc,
            "loss": epoch_loss
        })

    # モデル保存
    buffer = io.BytesIO()
    torch.save(model.state_dict(), buffer)
    model_blob = buffer.getvalue()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO models (id, weights, metadata)
        VALUES ('cnn', ?, ?)
    ''', (model_blob, f'{{"accuracy": {epoch_acc}}}'))
    conn.commit()
    conn.close()

    return {"accuracy": epoch_acc, "loss": epoch_loss}

def start_cnn_training_async(epochs: int, batch_size: int) -> str:
    """CNNトレーニングを非同期で開始"""
    task_id = str(uuid.uuid4())

    training_tasks[task_id] = {
        "status": "starting",
        "progress": 0,
        "epoch": 0,
        "totalEpochs": epochs,
        "accuracy": 0.0,
        "loss": 0.0
    }

    def progress_callback(info):
        training_tasks[task_id].update(info)

    def train_thread():
        try:
            result = train_cnn_model(epochs, batch_size, progress_callback)
            training_tasks[task_id]["status"] = "completed"
        except Exception as e:
            training_tasks[task_id]["status"] = "failed"
            training_tasks[task_id]["error"] = str(e)

    thread = threading.Thread(target=train_thread)
    thread.start()

    return task_id

def get_training_status(task_id: str) -> Dict:
    """トレーニング状況を取得"""
    return training_tasks.get(task_id)

def load_cnn_model():
    """保存されたCNNモデルをロード"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT weights FROM models WHERE id = 'cnn'")
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    model = DigitCNN()
    buffer = io.BytesIO(row[0])
    model.load_state_dict(torch.load(buffer, map_location='cpu'))
    model.eval()

    return model

# グローバルモデル（推論用）
_cnn_model = None

def predict_digit(image_data: List[float]) -> Dict:
    """数字を推論"""
    global _cnn_model

    if _cnn_model is None:
        _cnn_model = load_cnn_model()
        if _cnn_model is None:
            raise Exception("CNN model not trained yet")

    # 画像を準備
    image = np.array(image_data, dtype=np.float32).reshape(1, 1, 28, 28)
    image_tensor = torch.FloatTensor(image)

    # 推論
    with torch.no_grad():
        output = _cnn_model(image_tensor)
        probabilities = torch.softmax(output, dim=1)
        confidence, predicted = torch.max(probabilities, 1)

    return {
        "digit": predicted.item(),
        "confidence": confidence.item()
    }
