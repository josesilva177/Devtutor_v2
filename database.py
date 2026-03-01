import sqlite3
import hashlib
import os
from datetime import datetime


DB_PATH = "devtutor.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Cria as tabelas se não existirem"""
    conn = get_db()
    cursor = conn.cursor()

    # Tabela de utilizadores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Tabela de histórico de conversas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            provider TEXT,
            mode TEXT,
            response_time TEXT,
            tokens_used INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()
    print("Base de dados inicializada")


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(username: str, email: str, password: str):
    """Cria um novo utilizador. Retorna (ok, mensagem)"""
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username.strip(), email.strip().lower(), hash_password(password))
        )
        conn.commit()
        return True, "Conta criada com sucesso!"
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return False, "Nome de utilizador já existe"
        return False, "Email já está registado"
    finally:
        conn.close()


def login_user(username: str, password: str):
    """Verifica credenciais. Retorna (user_dict | None, mensagem)"""
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ? AND password_hash = ?",
        (username.strip(), hash_password(password))
    ).fetchone()
    conn.close()

    if user:
        return dict(user), "Login efetuado com sucesso!"
    return None, "Utilizador ou palavra-passe incorretos"


def save_history(user_id: int, question: str, answer: str, provider: str, mode: str, response_time: str, tokens_used: int):
    """Guarda uma conversa no histórico"""
    conn = get_db()
    conn.execute(
        """INSERT INTO history 
           (user_id, question, answer, provider, mode, response_time, tokens_used)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (user_id, question, answer, provider, mode, response_time, tokens_used)
    )
    conn.commit()
    conn.close()


def get_history(user_id: int, limit: int = 50):
    """Retorna histórico do utilizador"""
    conn = get_db()
    rows = conn.execute(
        """SELECT * FROM history WHERE user_id = ?
           ORDER BY created_at DESC LIMIT ?""",
        (user_id, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_history_item(history_id: int, user_id: int):
    """Apaga um item do histórico (só do próprio utilizador)"""
    conn = get_db()
    conn.execute(
        "DELETE FROM history WHERE id = ? AND user_id = ?",
        (history_id, user_id)
    )
    conn.commit()
    conn.close()


def clear_all_history(user_id: int):
    """Apaga todo o histórico do utilizador"""
    conn = get_db()
    conn.execute("DELETE FROM history WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()