"""Presentation-safe conversion and download helpers."""

from __future__ import annotations

import base64
from io import BytesIO
import zipfile

from PIL import Image

from utils.legacy_ui_results import build_evolution_stages, resolve_final_output


def decode_base64_image(value: str | None) -> Image.Image | None:
    if not value:
        return None
    try:
        payload = value.split(",", 1)[1] if "," in value else value
        with Image.open(BytesIO(base64.b64decode(payload))) as image:
            image.load()
            return image.copy()
    except (ValueError, TypeError, OSError):
        return None


def final_image(result: dict, mode: str) -> Image.Image | None:
    selection = resolve_final_output(result, exp_mode=mode)
    return decode_base64_image(result.get(selection.image_key)) if selection.image_key else None


def final_description(result: dict, mode: str) -> str:
    selection = resolve_final_output(result, exp_mode=mode)
    if not selection.text_key:
        return ""
    value = result.get(selection.text_key, "")
    return value if isinstance(value, str) else str(value)


def evolution_stages(result: dict, mode: str) -> list[dict]:
    return build_evolution_stages(result, exp_mode=mode)


def image_png_bytes(image: Image.Image) -> bytes:
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def candidate_zip(results: list[dict], mode: str) -> bytes:
    output = BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for index, result in enumerate(results, start=1):
            image = final_image(result, mode)
            if image is None:
                continue
            archive.writestr(
                f"paperbanana-candidate-{index:02d}.png",
                image_png_bytes(image),
            )
    return output.getvalue()

