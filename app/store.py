"""图像索引存储（SQLite，Day 2）。"""
import json
import os
import sqlite3
import time

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vision.db")
SCHEMA = """
CREATE TABLE IF NOT EXISTS image_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT,
    product_id INTEGER,
    path TEXT NOT NULL,
    embedding TEXT NOT NULL,
    created_at REAL NOT NULL
);
"""


def conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA)
    return c


def add(label: str, product_id: int | None, path: str, embedding: list[float]) -> int:
    c = conn()
    cur = c.execute(
        "INSERT INTO image_index (label, product_id, path, embedding, created_at) VALUES (?, ?, ?, ?, ?)",
        (label, product_id, path, json.dumps([float(x) for x in embedding]), time.time()),
    )
    c.commit()
    return cur.lastrowid


def all_rows():
    c = conn()
    return [dict(r) for r in c.execute("SELECT id, label, product_id, path, embedding FROM image_index").fetchall()]


def count() -> int:
    return conn().execute("SELECT count(*) c FROM image_index").fetchone()["c"]
