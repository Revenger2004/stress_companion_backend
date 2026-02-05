from typing import Dict, List

class SessionStore:
    def __init__(self):
        self._sessions: Dict[str, List[dict]] = {}

    def get(self, session_id: str) -> List[dict]:
        return self._sessions.get(session_id, [])

    def add(self, session_id: str, role: str, content: str) -> None:
        if session_id not in self._sessions:
            self._sessions[session_id] = []

        self._sessions[session_id].append({
            "role": role,
            "content": content
        })

    def clear(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)


session_store = SessionStore()
