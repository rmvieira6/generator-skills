import hashlib
import json
from typing import Any


def stable_hash(payload: Any) -> str:
    normalized = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def material_diff(old_payload: dict[str, Any], new_payload: dict[str, Any]) -> str:
    old_set = set(json.dumps(item, sort_keys=True) for item in old_payload.get("materials", []))
    new_set = set(json.dumps(item, sort_keys=True) for item in new_payload.get("materials", []))

    added = [json.loads(entry) for entry in sorted(new_set - old_set)]
    removed = [json.loads(entry) for entry in sorted(old_set - new_set)]

    return json.dumps({"added": added, "removed": removed}, ensure_ascii=True)
