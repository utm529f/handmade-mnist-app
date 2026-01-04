import sqlite3
from pathlib import Path

DB_PATH = Path("data/math_game.db")

def init_db():
    """データベース初期化"""
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # samples テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS samples (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        digit INTEGER NOT NULL,
        image_data BLOB NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_samples_digit ON samples(digit)')

    # models テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS models (
        id TEXT PRIMARY KEY,
        weights BLOB NOT NULL,
        metadata TEXT,
        trained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # game_history テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS game_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        correct_answer INTEGER NOT NULL,
        user_answer INTEGER NOT NULL,
        user_image_ones BLOB NOT NULL,
        user_image_tens BLOB,
        cnn_confidence REAL,
        correct BOOLEAN NOT NULL,
        response_time_ms INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()
