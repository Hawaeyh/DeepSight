"""Manual checkpoint inspection utility; not an automated pytest test."""

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a local PyTorch checkpoint type.")
    parser.add_argument("checkpoint", type=Path)
    args = parser.parse_args()
    if not args.checkpoint.is_file():
        print(f"Checkpoint not found: {args.checkpoint}")
        return 2

    import torch

    try:
        model = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    except Exception as error:
        print(f"Checkpoint inspection failed: {error}")
        return 1
    print(type(model).__name__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
