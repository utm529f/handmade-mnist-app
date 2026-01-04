# てづくりMNIST - FastAPI Backend

子ども向けの手書き数字機械学習アプリケーションのバックエンドAPI

## 概要

このプロジェクトは、子どもたちが自分で手書きした数字でAIを学習させ、算数ゲームで遊べるWebアプリケーションのバックエンドです。

### 主な機能

1. **データ収集**: 手書き数字（0-9）の画像データを保存
2. **機械学習**: PyTorchを使用したCNNモデルの学習
3. **ゲーム**: 手書き数字を使った算数ゲーム（たしざん・ひきざん）

## 技術スタック

- **FastAPI**: 高速なPython Webフレームワーク
- **PyTorch**: ディープラーニングフレームワーク
- **SQLite**: 軽量データベース
- **Pydantic**: データバリデーション

## セットアップ

### 必要要件

- Python 3.9以上
- pip

### インストール

1. リポジトリをクローン

```bash
cd handmade-mnist-fastapi
```

2. 依存関係をインストール

```bash
pip install -r backend/requirements.txt
```

### バックエンドサーバー起動

```bash
cd backend
uvicorn main:app --reload
```

サーバーは `http://localhost:8000` で起動します。

### API ドキュメント

起動後、以下のURLでインタラクティブなAPIドキュメントにアクセスできます：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### フロントエンド起動

フロントエンドは静的HTMLファイルなので、シンプルなHTTPサーバーで起動できます：

**Python を使う場合：**
```bash
cd frontend
python -m http.server 8080
```

**Node.js の http-server を使う場合：**
```bash
cd frontend
npx http-server -p 8080
```

フロントエンドは `http://localhost:8080` で起動します。

**注意:** バックエンド（port 8000）とフロントエンド（port 8080）の両方を起動する必要があります。

## API エンドポイント

### データ収集API

#### POST /api/samples
手書き数字サンプルを保存

```json
{
  "digit": 5,
  "imageData": [0.0, 0.1, ..., 0.9]  // 784個の float値 (28x28)
}
```

#### GET /api/samples/status
データ収集状況を取得

レスポンス:
```json
{
  "valid": true,
  "total": 100,
  "perDigit": [10, 10, 10, 10, 10, 10, 10, 10, 10, 10],
  "missingDigits": []
}
```

#### GET /api/samples/digit/{digit}
指定した数字のランダムサンプルを取得

### モデル学習API

#### POST /api/train/cnn
CNN学習を開始

```json
{
  "epochs": 20,
  "batchSize": 16
}
```

レスポンス:
```json
{
  "status": "training_started",
  "taskId": "uuid-string"
}
```

#### GET /api/train/cnn/status/{taskId}
学習状況を取得

レスポンス:
```json
{
  "status": "training",
  "progress": 50,
  "epoch": 10,
  "totalEpochs": 20,
  "accuracy": 0.85,
  "loss": 0.15
}
```

#### GET /api/models/status
学習済みモデルの状況を取得

### ゲームAPI

#### POST /api/game/question
新しい問題を生成

```json
{
  "mode": "mixed"  // "add", "subtract", "mixed"
}
```

レスポンス:
```json
{
  "questionId": "uuid-string",
  "num1": 3,
  "num2": 5,
  "num1Image": [...],
  "num2Image": [...],
  "operator": "+",
  "answer": 8,
  "is2Digit": false
}
```

#### POST /api/game/answer
回答を送信

```json
{
  "questionId": "uuid-string",
  "onesImageData": [...],
  "tensImageData": null
}
```

レスポンス:
```json
{
  "recognizedAnswer": 8,
  "correct": true,
  "confidence": 0.95,
  "correctAnswer": 8
}
```

#### GET /api/game/history
ゲーム履歴を取得

## ディレクトリ構造

```
handmade-mnist-fastapi/
├── backend/
│   ├── main.py          # FastAPI アプリケーション
│   ├── database.py      # SQLite データベース設定
│   ├── schemas.py       # Pydantic スキーマ定義
│   ├── crud.py          # データベース操作
│   ├── models.py        # PyTorch モデル定義
│   ├── train.py         # 学習・推論ロジック
│   └── requirements.txt # Python依存関係
├── frontend/
│   ├── index.html       # メニュー画面
│   ├── collect.html     # データ収集画面
│   ├── train.html       # モデル学習画面
│   ├── game.html        # ゲーム画面
│   ├── js/
│   │   ├── api.js       # API通信処理
│   │   └── canvas.js    # Canvas描画処理
│   └── css/
│       └── style.css    # スタイルシート
├── data/
│   └── math_game.db     # SQLite データベース（自動生成）
└── README.md
```

## データベーススキーマ

### samples テーブル
手書き数字サンプル

- `id`: INTEGER PRIMARY KEY
- `digit`: INTEGER (0-9)
- `image_data`: BLOB (28x28画像データ)
- `created_at`: TIMESTAMP

### models テーブル
学習済みモデル

- `id`: TEXT PRIMARY KEY ('cnn' or 'vae')
- `weights`: BLOB (モデルの重み)
- `metadata`: TEXT (JSON形式のメタデータ)
- `trained_at`: TIMESTAMP

### game_history テーブル
ゲーム履歴

- `id`: INTEGER PRIMARY KEY
- `question`: TEXT
- `correct_answer`: INTEGER
- `user_answer`: INTEGER
- `user_image_ones`: BLOB
- `user_image_tens`: BLOB
- `cnn_confidence`: REAL
- `correct`: BOOLEAN
- `created_at`: TIMESTAMP

## 開発

### デバッグモードで起動

```bash
uvicorn main:app --reload --log-level debug
```

### テスト

```bash
# 手動テスト用のサンプルデータ生成
python -c "
import requests
import numpy as np

# サンプルデータ作成（28x28のランダム画像）
image_data = np.random.rand(784).tolist()

# サンプル保存
response = requests.post('http://localhost:8000/api/samples', json={
    'digit': 5,
    'imageData': image_data
})
print(response.json())
"
```

## デプロイ

### Render へのデプロイ

1. Renderアカウントを作成
2. 新しいWeb Serviceを作成
3. ビルドコマンド: `pip install -r backend/requirements.txt`
4. スタートコマンド: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

## ライセンス

MIT License