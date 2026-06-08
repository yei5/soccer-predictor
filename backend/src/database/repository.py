import json
import os
from typing import List, Dict, Any
from .connection import db_manager
from ..config.settings import settings

class ChatRepository:
    @staticmethod
    def create_session(title: str = "New Analysis") -> int:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO sessions (title) VALUES (?)', (title,))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def add_message(session_id: int, role: str, content: str, prediction_data: Any = None):
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            pred_json = json.dumps(prediction_data) if prediction_data else None
            cursor.execute('''
                INSERT INTO messages (session_id, role, content, prediction_data)
                VALUES (?, ?, ?, ?)
            ''', (session_id, role, content, pred_json))
            conn.commit()

    @staticmethod
    def get_sessions() -> List[Dict[str, Any]]:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM sessions ORDER BY created_at DESC')
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_messages(session_id: int) -> List[Dict[str, Any]]:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM messages WHERE session_id = ? ORDER BY created_at ASC', (session_id,))
            rows = cursor.fetchall()
            messages = []
            for row in rows:
                msg = dict(row)
                if msg['prediction_data']:
                    msg['prediction_data'] = json.loads(msg['prediction_data'])
                messages.append(msg)
            return messages

    @staticmethod
    def update_session_title(session_id: int, title: str):
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE sessions SET title = ? WHERE id = ?', (title, session_id))
            conn.commit()

    @staticmethod
    def session_exists(session_id: int) -> bool:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM sessions WHERE id = ?', (session_id,))
            return cursor.fetchone() is not None

class HistoricalMatchRepository:
    def __init__(self, file_path: str = None):
        self.file_path = file_path or settings.HISTORICAL_DATA_PATH
        self.matches = []
        self._load_data()

    def _load_data(self):
        if not os.path.exists(self.file_path):
            return
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if not lines: return
                headers = lines[0].strip().split('::')
                for line in lines[1:]:
                    parts = line.strip().split('::')
                    if len(parts) == len(headers):
                        self.matches.append(dict(zip(headers, parts)))
        except Exception as e:
            print(f"Error loading historical data: {e}")

    def get_h2h(self, team1_name: str, team2_name: str) -> List[Dict[str, Any]]:
        t1 = team1_name.lower().replace("fc ", "").replace(" real", "").strip()
        t2 = team2_name.lower().replace("fc ", "").replace(" real", "").strip()
        
        mappings = {
            "athletic club": "atletico de bilbao",
            "atletico madrid": "atletico de madrid",
            "valencia cf": "valencia",
            "rcd espanyol": "espanol",
            "malaga cf": "cd malaga"
        }
        t1 = mappings.get(t1, t1)
        t2 = mappings.get(t2, t2)

        results = []
        for m in self.matches:
            local = m['EquipoLocal'].lower()
            visitante = m['EquipoVisitante'].lower()
            if (t1 in local and t2 in visitante) or (t2 in local and t1 in visitante):
                results.append(m)
        return results[-20:]
