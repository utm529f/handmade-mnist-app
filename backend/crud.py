import sqlite3
import numpy as np
import random
import uuid
from typing import List, Optional, Dict
from pathlib import Path
from database import DB_PATH
import torch
import io

def save_sample(digit: int, image_data: List[float]) -> int:
    """サンプルを保存"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Float32Arrayをバイナリに変換
    image_array = np.array(image_data, dtype=np.float32)
    image_blob = image_array.tobytes()

    cursor.execute(
        "INSERT INTO samples (digit, image_data) VALUES (?, ?)",
        (digit, image_blob)
    )
    sample_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return sample_id

def get_data_status() -> Dict:
    """データ収集状況を取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 数字ごとのカウント
    per_digit = []
    for digit in range(10):
        cursor.execute("SELECT COUNT(*) FROM samples WHERE digit = ?", (digit,))
        count = cursor.fetchone()[0]
        per_digit.append(count)

    total = sum(per_digit)

    # 条件チェック: 各数字3枚以上 & 合計30枚以上
    missing_digits = [d for d in range(10) if per_digit[d] < 3]
    valid = len(missing_digits) == 0 and total >= 30

    conn.close()

    return {
        "valid": valid,
        "total": total,
        "perDigit": per_digit,
        "missingDigits": missing_digits
    }

def get_random_sample_by_digit(digit: int) -> Optional[Dict]:
    """指定した数字のランダムサンプルを取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, digit, image_data FROM samples WHERE digit = ? ORDER BY RANDOM() LIMIT 1",
        (digit,)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    # BLOBからFloat32Arrayに変換
    image_array = np.frombuffer(row[2], dtype=np.float32)

    return {
        "id": row[0],
        "digit": row[1],
        "imageData": image_array.tolist()
    }

def get_models_status() -> Dict:
    """モデルの学習状況を取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cnn_status = {"trained": False, "trainedAt": None}
    vae_status = {"trained": False, "trainedAt": None}

    cursor.execute("SELECT id, trained_at, metadata FROM models WHERE id = 'cnn'")
    cnn_row = cursor.fetchone()
    if cnn_row:
        cnn_status = {"trained": True, "trainedAt": cnn_row[1], "metadata": cnn_row[2]}

    cursor.execute("SELECT id, trained_at, metadata FROM models WHERE id = 'vae'")
    vae_row = cursor.fetchone()
    if vae_row:
        vae_status = {"trained": True, "trainedAt": vae_row[1], "metadata": vae_row[2]}

    conn.close()

    return {
        "cnn": cnn_status,
        "vae": vae_status
    }

# ゲーム関連の一時データ
active_questions = {}

def generate_question(mode: str = "mixed") -> Dict:
    """問題を生成"""
    # ランダムで加算または減算を選択
    operator = random.choice(['+', '-'])

    if operator == '+':
        num1 = random.randint(0, 9)
        num2 = random.randint(0, 9 - num1)  # 答えが0-9になるように
        answer = num1 + num2
    else:  # '-'
        num1 = random.randint(0, 9)
        num2 = random.randint(0, num1)  # 負にならないように
        answer = num1 - num2

    # 画像をランダム取得
    num1_sample = get_random_sample_by_digit(num1)
    num2_sample = get_random_sample_by_digit(num2)

    if not num1_sample or not num2_sample:
        raise Exception("Insufficient sample data")

    question_id = str(uuid.uuid4())

    question_data = {
        "questionId": question_id,
        "num1": num1,
        "num2": num2,
        "num1Image": num1_sample["imageData"],
        "num2Image": num2_sample["imageData"],
        "operator": operator,
        "answer": answer,
        "is2Digit": False  # 常に1桁
    }

    # アクティブな問題として保存
    active_questions[question_id] = question_data

    return question_data

def check_answer(answer_request) -> Dict:
    """回答をチェック"""
    question_id = answer_request.questionId

    if question_id not in active_questions:
        raise Exception("Question not found")

    question = active_questions[question_id]

    # CNN推論を実行（後で実装）
    from train import predict_digit

    ones_pred = predict_digit(answer_request.onesImageData)
    recognized_answer = ones_pred["digit"]
    confidence = ones_pred["confidence"]

    correct = recognized_answer == question["answer"]

    # 履歴に保存
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    ones_blob = np.array(answer_request.onesImageData, dtype=np.float32).tobytes()
    tens_blob = None

    cursor.execute('''
        INSERT INTO game_history
        (question, correct_answer, user_answer, user_image_ones, user_image_tens, cnn_confidence, correct)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        f"{question['num1']} {question['operator']} {question['num2']}",
        question["answer"],
        recognized_answer,
        ones_blob,
        tens_blob,
        confidence,
        correct
    ))

    conn.commit()
    conn.close()

    # アクティブ問題から削除
    del active_questions[question_id]

    return {
        "recognizedAnswer": recognized_answer,
        "correct": correct,
        "confidence": confidence,
        "correctAnswer": question["answer"]
    }

def get_game_history(limit: int = 50) -> List[Dict]:
    """ゲーム履歴を取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT question, correct_answer, user_answer, correct, cnn_confidence, created_at
        FROM game_history
        ORDER BY created_at DESC
        LIMIT ?
    ''', (limit,))

    rows = cursor.fetchall()
    conn.close()

    history = []
    for row in rows:
        history.append({
            "question": row[0],
            "correctAnswer": row[1],
            "userAnswer": row[2],
            "correct": bool(row[3]),
            "confidence": row[4],
            "createdAt": row[5]
        })

    return history
