/**
 * FastAPI バックエンドとの通信処理
 */

// API base URL (開発環境とプロダクションで切り替え)
const API_BASE_URL = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : 'https://handmade-mnist-backend.onrender.com';

/**
 * サンプルデータを保存
 * @param {number} digit - 数字 (0-9)
 * @param {Float32Array} imageData - 28x28画像データ
 * @returns {Promise<Object>} レスポンス
 */
async function saveSample(digit, imageData) {
  const response = await fetch(`${API_BASE_URL}/api/samples`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      digit: digit,
      imageData: Array.from(imageData)
    })
  });

  if (!response.ok) {
    throw new Error(`Failed to save sample: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * データ収集状況を取得
 * @returns {Promise<Object>} { valid, total, perDigit, missingDigits }
 */
async function checkDataRequirements() {
  const response = await fetch(`${API_BASE_URL}/api/samples/status`);

  if (!response.ok) {
    throw new Error(`Failed to get data status: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Reset all data (samples, models, game history)
 * @returns {Promise<Object>} Response message
 */
async function resetAllData() {
  const response = await fetch(`${API_BASE_URL}/api/data/reset`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    throw new Error(`Failed to reset data: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * 指定した数字のランダムサンプルを取得
 * @param {number} digit - 数字 (0-9)
 * @returns {Promise<Object>} { id, digit, imageData }
 */
async function getSampleByDigit(digit) {
  const response = await fetch(`${API_BASE_URL}/api/samples/digit/${digit}`);

  if (!response.ok) {
    if (response.status === 404) {
      return null;
    }
    throw new Error(`Failed to get sample: ${response.statusText}`);
  }

  const data = await response.json();
  return {
    id: data.id,
    digit: data.digit,
    imageData: new Float32Array(data.imageData)
  };
}

/**
 * CNN学習を開始
 * @param {number} epochs - エポック数
 * @param {number} batchSize - バッチサイズ
 * @returns {Promise<Object>} { status, taskId }
 */
async function startCNNTraining(epochs = 20, batchSize = 16) {
  const response = await fetch(`${API_BASE_URL}/api/train/cnn`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      epochs: epochs,
      batchSize: batchSize
    })
  });

  if (!response.ok) {
    throw new Error(`Failed to start training: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * 学習状況を取得
 * @param {string} taskId - タスクID
 * @returns {Promise<Object>} { status, progress, epoch, totalEpochs, accuracy, loss }
 */
async function getTrainingStatus(taskId) {
  const response = await fetch(`${API_BASE_URL}/api/train/cnn/status/${taskId}`);

  if (!response.ok) {
    if (response.status === 404) {
      return null;
    }
    throw new Error(`Failed to get training status: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * モデルの学習状況を取得
 * @returns {Promise<Object>} { cnn: {...}, vae: {...} }
 */
async function getModelsStatus() {
  const response = await fetch(`${API_BASE_URL}/api/models/status`);

  if (!response.ok) {
    throw new Error(`Failed to get models status: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * 新しい問題を生成
 * @param {string} mode - "add", "subtract", "mixed"
 * @returns {Promise<Object>} 問題データ
 */
async function generateQuestion(mode = "mixed") {
  const response = await fetch(`${API_BASE_URL}/api/game/question`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ mode: mode })
  });

  if (!response.ok) {
    throw new Error(`Failed to generate question: ${response.statusText}`);
  }

  const data = await response.json();

  // imageData を Float32Array に変換
  return {
    ...data,
    num1Image: new Float32Array(data.num1Image),
    num2Image: new Float32Array(data.num2Image)
  };
}

/**
 * 回答を送信
 * @param {string} questionId - 問題ID
 * @param {Float32Array} onesImageData - 1の位の画像データ
 * @param {Float32Array|null} tensImageData - 10の位の画像データ
 * @returns {Promise<Object>} { recognizedAnswer, correct, confidence, correctAnswer }
 */
async function submitAnswer(questionId, onesImageData, tensImageData = null) {
  const response = await fetch(`${API_BASE_URL}/api/game/answer`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      questionId: questionId,
      onesImageData: Array.from(onesImageData),
      tensImageData: tensImageData ? Array.from(tensImageData) : null
    })
  });

  if (!response.ok) {
    throw new Error(`Failed to submit answer: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * ゲーム履歴を取得
 * @returns {Promise<Array>} 履歴データ
 */
async function getGameHistory() {
  const response = await fetch(`${API_BASE_URL}/api/game/history`);

  if (!response.ok) {
    throw new Error(`Failed to get game history: ${response.statusText}`);
  }

  const data = await response.json();
  return data.history;
}
