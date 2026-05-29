from collections import defaultdict
from config import SESSION_MEMORY_TURNS

_sessions: dict[str, list[dict]] = defaultdict(list)


def get_history(session_id: str) -> list[dict]:
    return _sessions[session_id]


def add_turn(session_id: str, role: str, content: str):
    _sessions[session_id].append({"role": role, "content": content})
    if len(_sessions[session_id]) > SESSION_MEMORY_TURNS * 2:
        _sessions[session_id] = _sessions[session_id][-(SESSION_MEMORY_TURNS * 2):]


def clear_session(session_id: str):
    _sessions.pop(session_id, None)
