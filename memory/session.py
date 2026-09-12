from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from pathlib import Path

from config import config

MEMORY_PATH = Path(config["memory"]["base_path"])
MEMORY_PATH.mkdir(parents=True, exist_ok=True)

SESSIONS_FILE = MEMORY_PATH / "sessions.json"


@dataclass(slots=True)
class Session:
    id: str
    name: str
    path: Path


class SessionManager:

    def __init__(self):
        self._ensure_file()

    def _ensure_file(self):
        if not SESSIONS_FILE.exists():
            SESSIONS_FILE.write_text("[]", encoding="utf-8")

    def _load(self):
        return json.loads(SESSIONS_FILE.read_text(encoding="utf-8"))

    def _save(self, sessions):
        SESSIONS_FILE.write_text(
            json.dumps(sessions, indent=4),
            encoding="utf-8",
        )

    def create(self, name: str | None = None) -> Session:

        session_id = str(uuid.uuid4())

        if name is None:
            name = f"Session-{session_id[:8]}"

        path = MEMORY_PATH / session_id
        path.mkdir(parents=True, exist_ok=True)

        sessions = self._load()

        sessions.append(
            {
                "id": session_id,
                "name": name,
            }
        )

        self._save(sessions)

        return Session(
            id=session_id,
            name=name,
            path=path,
        )

    def list(self) -> list[Session]:

        sessions = self._load()

        return [
            Session(
                id=s["id"],
                name=s["name"],
                path=MEMORY_PATH / s["id"],
            )
            for s in sessions
        ]

    def switch(self, session_id: str) -> Session:

        for session in self.list():

            if session.id == session_id:
                return session

        raise ValueError(f"Session '{session_id}' not found.")