from src.core.config import settings
from src.domain.entities import Material


SENSITIVE_KEYS = {
    "password",
    "token",
    "secret",
    "api_key",
    "access_key",
    "secret_key",
    "service_account_json",
}


def validate_materials(materials: list[Material]) -> list[Material]:
    if len(materials) > settings.MAX_MATERIALS_PER_PROJECT:
        raise ValueError(
            f"Too many materials: {len(materials)}. Max is {settings.MAX_MATERIALS_PER_PROJECT}."
        )

    validated: list[Material] = []
    for material in materials:
        if not material.description.strip():
            raise ValueError(f"Material '{material.name}' must include a description")

        validated.append(material)

    return validated


def sanitize_metadata(metadata: dict[str, str | int | bool | None]) -> dict[str, str | int | bool | None]:
    clean: dict[str, str | int | bool | None] = {}
    for key, value in metadata.items():
        if key.lower() in SENSITIVE_KEYS:
            continue
        clean[key] = value
    return clean
