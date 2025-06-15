from dataclasses import dataclass
from datetime import datetime

__all__ = [
    "User",
    "Subscription",
    "Token",
    "Config",
    "SCHEMA",
]

# SQLite schema definitions and data models

@dataclass
class User:
    id: int
    username: str
    full_name: str
    is_admin: bool


@dataclass
class Subscription:
    user_id: int
    start_date: datetime
    end_date: datetime


@dataclass
class Token:
    token: str
    duration_days: int
    used: bool


@dataclass
class Config:
    key: str
    value: str

# SQL commands to create tables
SCHEMA = """
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    is_admin INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS subscription (
    user_id INTEGER NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS token (
    token TEXT PRIMARY KEY,
    duration_days INTEGER NOT NULL,
    used INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""
