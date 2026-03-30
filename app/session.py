from datetime import datetime, timezone
import threading

class SessionTracker:
    def __init__(self):
        self._sessions: dict[str, dict] = {}
        self._lock = threading.Lock()
    
    def record(self, ip: str, sector: str) -> None:
        with self._lock:
            if ip not in self._sessions:
                self._sessions[ip] = {
                    "request_count": 0,
                    "sectors_queried": [],
                    "first_request": datetime.now(timezone.utc), 
                    "last_request": datetime.now(timezone.utc),
                }
            session = self._sessions[ip]
            session["request_count"] += 1
            session["last_request"] = datetime.now(timezone.utc)
            if sector not in session["sectors_queried"]:
                session["sectors_queried"].append(sector)
    
    def get(self, ip: str) -> dict | None:
        return self._sessions.get(ip)
    
    def all_sessions(self) -> dict:
        return dict(self._sessions)

session_tracker = SessionTracker()
