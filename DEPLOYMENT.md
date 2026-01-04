# デプロイメントガイド

てづくりMNIST アプリケーションの公開手順

## 目次

1. [事前準備](#事前準備)
2. [GitHubへの公開](#githubへの公開)
3. [バックエンドのデプロイ](#バックエンドのデプロイ)
4. [フロントエンドのデプロイ](#フロントエンドのデプロイ)
5. [動作確認](#動作確認)

---

## 事前準備

### 必要なアカウント

以下のサービスのアカウントを作成してください（すべて無料プランで利用可能）：

- [GitHub](https://github.com/) - コード管理
- [Render](https://render.com/) - バックエンドホスティング（推奨）
- [Vercel](https://vercel.com/) または [Netlify](https://www.netlify.com/) - フロントエンドホスティング

### 必要なツール

```bash
# Git（バージョン確認）
git --version

# GitHub CLIのインストール（オプションだが推奨）
# Windows: https://cli.github.com/
# Mac: brew install gh
```

---

## GitHubへの公開

### 1. .gitignoreファイルの作成

プロジェクトルートに`.gitignore`ファイルを作成：

```bash
cd handmade-mnist-fastapi
```

`.gitignore`の内容：

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# データベース
*.db
*.sqlite
*.sqlite3
data/*.db

# モデルファイル
*.pth
*.pt
models/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# 環境変数
.env
.env.local

# ログ
*.log

# エラー画像（開発用）
error*.png
```

### 2. Gitリポジトリの初期化

```bash
# Gitリポジトリを初期化
git init

# ファイルをステージング
git add .

# 初回コミット
git commit -m "Initial commit: 手書き数字機械学習アプリ"
```

### 3. GitHubリポジトリの作成とプッシュ

**方法A: GitHub CLI を使用（推奨）**

```bash
# GitHub CLIでログイン
gh auth login

# リポジトリを作成してプッシュ
gh repo create handmade-mnist-app --public --source=. --push
```

**方法B: GitHub Web UIを使用**

1. [GitHub](https://github.com/new)で新しいリポジトリを作成
2. リポジトリ名: `handmade-mnist-app` （任意）
3. Public/Privateを選択
4. READMEは追加しない（既に存在するため）
5. 以下のコマンドを実行：

```bash
git remote add origin https://github.com/YOUR_USERNAME/handmade-mnist-app.git
git branch -M main
git push -u origin main
```

---

## バックエンドのデプロイ

### Render.comを使用したデプロイ

#### 1. Renderの準備

1. [Render.com](https://render.com/)にサインアップ
2. GitHubアカウントと連携

#### 2. 新しいWeb Serviceの作成

1. Renderダッシュボードで「New +」→「Web Service」をクリック
2. GitHubリポジトリ`handmade-mnist-app`を選択
3. 以下の設定を入力：

| 項目 | 値 |
|------|-----|
| Name | `handmade-mnist-backend` |
| Region | `Singapore` または `Oregon`（お好みで） |
| Branch | `main` |
| Root Directory | `backend` |
| Runtime | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Instance Type | `Free` |

#### 3. 環境変数の設定（オプション）

必要に応じて以下を設定：

- `PYTHON_VERSION`: `3.11.0`
- `ENVIRONMENT`: `production`

#### 4. デプロイの実行

「Create Web Service」をクリックすると自動的にデプロイが開始されます。

#### 5. バックエンドURLの確認

デプロイが完了すると、以下のようなURLが発行されます：

```
https://handmade-mnist-backend.onrender.com
```

このURLをメモしておきます（フロントエンドの設定で使用）。

#### トラブルシューティング

**デプロイに失敗する場合：**

1. ログを確認して、依存関係のエラーがないかチェック
2. `requirements.txt`のバージョンを確認
3. Pythonバージョンを環境変数で明示

**無料プランの注意点：**

- 15分間アクセスがないとスリープモードに入る
- 初回アクセス時は起動に30秒〜1分程度かかる

---

## フロントエンドのデプロイ

### Vercelを使用したデプロイ（推奨）

#### 1. API URLの更新

フロントエンドのAPI通信先を本番環境用に更新します。

`frontend/js/api.js`を編集：

```javascript
// 本番環境のバックエンドURLに変更
const API_BASE_URL = 'https://handmade-mnist-backend.onrender.com';
```

変更をコミット：

```bash
git add frontend/js/api.js
git commit -m "Update API URL for production"
git push
```

#### 2. Vercelでデプロイ

1. [Vercel](https://vercel.com/)にサインアップ
2. GitHubアカウントと連携
3. 「Add New Project」をクリック
4. `handmade-mnist-app`リポジトリを選択
5. 以下の設定を入力：

| 項目 | 値 |
|------|-----|
| Framework Preset | `Other` |
| Root Directory | `frontend` |
| Build Command | （空欄） |
| Output Directory | `./` |

6. 「Deploy」をクリック

#### 3. デプロイ完了

以下のようなURLが発行されます：

```
https://handmade-mnist-app.vercel.app
```

### Netlifyを使用したデプロイ（代替案）

#### 1. netlify.tomlの作成

`frontend/netlify.toml`を作成：

```toml
[build]
  publish = "."

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

#### 2. Netlifyでデプロイ

1. [Netlify](https://www.netlify.com/)にサインアップ
2. 「Add new site」→「Import an existing project」
3. GitHubリポジトリを選択
4. 設定：
   - Base directory: `frontend`
   - Build command: （空欄）
   - Publish directory: `.`
5. 「Deploy site」をクリック

---

## CORS設定の調整

バックエンドがフロントエンドからのリクエストを受け付けるように、CORS設定を確認します。

`backend/main.py`で以下を確認：

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "https://handmade-mnist-app.vercel.app",  # Vercelのドメイン
        # または
        "https://YOUR_SITE.netlify.app"  # Netlifyのドメイン
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

変更した場合は再度プッシュしてRenderで自動デプロイされるのを待ちます。

---

## 動作確認

### 1. バックエンドの確認

ブラウザで以下のURLにアクセス：

```
https://handmade-mnist-backend.onrender.com/docs
```

Swagger UIが表示されれば成功です。

### 2. フロントエンドの確認

```
https://handmade-mnist-app.vercel.app
```

にアクセスして、アプリが正常に動作することを確認：

1. データ収集画面で数字を描画して保存
2. 学習画面でモデルを学習
3. ゲーム画面でゲームをプレイ

### 3. API通信の確認

ブラウザの開発者ツール（F12）を開いて：

1. Networkタブを確認
2. API通信が正常に行われているか確認
3. CORSエラーが出ていないか確認

---

## トラブルシューティング

### CORSエラーが発生する

```
Access to fetch at 'https://...' from origin 'https://...' has been blocked by CORS policy
```

**解決方法：**

1. `backend/main.py`の`allow_origins`にフロントエンドのURLを追加
2. 変更をプッシュしてRenderの再デプロイを待つ

### バックエンドが起動しない

**確認事項：**

1. Renderのログを確認
2. `requirements.txt`の依存関係を確認
3. `Start Command`が正しいか確認

### データベースがリセットされる

**原因：**

無料プランでは永続ストレージが提供されないため、再デプロイ時にデータが消えます。

**解決方法：**

1. Renderの有料プラン（$7/月〜）でPersistent Diskを追加
2. または外部データベース（PostgreSQL等）を使用

---

## 継続的デプロイメント

GitHubにプッシュすると自動的に以下が実行されます：

- **Render**: バックエンドの自動ビルド＆デプロイ
- **Vercel/Netlify**: フロントエンドの自動ビルド＆デプロイ

### デプロイフロー

```bash
# 1. 開発作業
git add .
git commit -m "新機能を追加"

# 2. GitHubにプッシュ
git push

# 3. 自動デプロイが実行される（数分待つ）

# 4. 本番環境で確認
```

---

## セキュリティのベストプラクティス

### 1. 環境変数の使用

機密情報はハードコーディングせず、環境変数を使用：

```python
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/math_game.db")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
```

### 2. HTTPS の使用

Render、Vercel、Netlifyはすべて自動的にHTTPSを提供します。

### 3. APIレート制限

本番環境では、FastAPIにレート制限を追加することを推奨：

```bash
pip install slowapi
```

---

## カスタムドメインの設定（オプション）

### バックエンド（Render）

1. Renderダッシュボードで「Settings」→「Custom Domain」
2. 独自ドメインを追加（例：`api.yourdomain.com`）
3. DNSレコードを設定

### フロントエンド（Vercel）

1. Vercelダッシュボードで「Settings」→「Domains」
2. カスタムドメインを追加（例：`app.yourdomain.com`）
3. DNSレコードを設定

---

## サポート

デプロイに関する質問や問題が発生した場合：

1. [GitHub Issues](https://github.com/YOUR_USERNAME/handmade-mnist-app/issues)で報告
2. 各プラットフォームのドキュメントを参照：
   - [Render Docs](https://render.com/docs)
   - [Vercel Docs](https://vercel.com/docs)
   - [Netlify Docs](https://docs.netlify.com/)

---

## 次のステップ

- データベースの永続化（PostgreSQL等への移行）
- ユーザー認証の追加
- モデルのバージョン管理
- パフォーマンスの最適化
- モニタリング＆ログ管理の設定

---

**おめでとうございます！** てづくりMNISTアプリが世界中に公開されました。
