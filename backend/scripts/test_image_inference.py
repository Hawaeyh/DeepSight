#!/usr/bin/env python3
"""Validate one local image and exercise the real configured image models."""
from __future__ import annotations

import argparse
import asyncio
import json
import mimetypes
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from fastapi import UploadFile
from starlette.datastructures import Headers

from app.ai.model_status import MODEL_ROOT, MODEL_SPECS
from app.services.ai_service import AIService
from app.services.image_validation_service import ImageValidationService


async def run(image: Path, model: str) -> int:
    if not image.is_file():
        print(f"Image does not exist: {image.name}", file=sys.stderr)
        return 2
    for key, spec in MODEL_SPECS.items():
        print(f"binary model {key}: {spec['checkpoint'].name} ({'available' if spec['checkpoint'].is_file() else 'missing'})")
    multiclass = MODEL_ROOT / "multiclass" / "efficientnet_b0_multiclass_best.pth"
    print(f"multiclass model: {multiclass.name} ({'available' if multiclass.is_file() else 'missing'})")
    content_type = mimetypes.guess_type(image.name)[0] or "application/octet-stream"
    with image.open("rb") as stream:
        upload = UploadFile(file=stream, filename=image.name, headers=Headers({"content-type": content_type}))
        validated = await ImageValidationService.validate_and_store(upload, "smoke-test")
    try:
        result = AIService.analyze_image(str(validated.path), model)
        print(json.dumps(result, indent=2, allow_nan=False))
        print("native result types:", {key: type(value).__name__ for key, value in result.items()})
        return 0 if result.get("success") else 3
    finally:
        validated.path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument("--model", choices=tuple(MODEL_SPECS), default="efficientnet")
    arguments = parser.parse_args()
    return asyncio.run(run(arguments.image.resolve(), arguments.model))


if __name__ == "__main__":
    raise SystemExit(main())
