"""Inspect official prompt-free YOLOE vocabulary without editing checkpoints."""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ml/pretrained/.runtime"))

from ultralytics import YOLOE  # noqa: E402


def main():
    weights = ROOT / "ml/pretrained/yoloe-26n-seg-pf.pt"
    model = YOLOE(str(weights))
    names = model.names
    terms = ("stair", "step", "pole", "pothole", "curb", "sidewalk", "ramp")
    matches = {term: {str(index): name for index, name in names.items()
                      if term in name.casefold()}
               for term in terms}
    print(json.dumps({"checkpoint": weights.name,
                      "sha256": hashlib.sha256(weights.read_bytes()).hexdigest(),
                      "class_count": len(names), "matches": matches}, indent=2))


if __name__ == "__main__":
    main()
