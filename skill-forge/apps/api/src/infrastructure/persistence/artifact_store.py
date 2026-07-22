import time
import uuid


class ArtifactStore:
    def __init__(self) -> None:
        self._store: dict[str, tuple[bytes, float]] = {}

    def put(self, data: bytes, ttl_seconds: int = 3600) -> str:
        token = str(uuid.uuid4())
        self._store[token] = (data, time.time() + ttl_seconds)
        self._purge_expired()
        return token

    def get(self, token: str) -> bytes | None:
        self._purge_expired()
        payload = self._store.get(token)
        if payload is None:
            return None
        return payload[0]

    def _purge_expired(self) -> None:
        now = time.time()
        expired = [token for token, (_, expires_at) in self._store.items() if expires_at < now]
        for token in expired:
            del self._store[token]


artifact_store = ArtifactStore()
