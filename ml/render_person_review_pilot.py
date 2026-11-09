"""Draw first-batch person proposals at source resolution for visual review."""

import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "runs/public_phase1_v15_oi_quarantine/person_draft_960"
SOURCE = ROOT / "data/processed/public_phase1_v15_oi_quarantine/images/train"
OUT = RUN / "pilot_review_overlays"
IDS = ["1271622877a21c47", "17d51251e2ce55f0", "5da1151716ece103",
       "654c3cb2305ea843", "69880732bf53c286"]


def main():
    rows = {row["image_id"]: row for row in json.loads((RUN / "draft_v18_179.json")
            .read_text(encoding="utf-8"))["rows"]}
    OUT.mkdir(parents=True, exist_ok=True)
    for image_id in IDS:
        row = rows[image_id]
        image = Image.open(SOURCE / f"oi_v10_train_{image_id}.jpg").convert("RGB")
        draw = ImageDraw.Draw(image)
        for index, proposal in enumerate(row["proposals"], 1):
            xyxy = proposal["xyxy_pixels"]
            draw.rectangle(tuple(xyxy), outline="#ff0033", width=5)
            draw.text((xyxy[0], max(0, xyxy[1] - 20)), str(index), fill="#ff0033")
        image.save(OUT / f"{image_id}.jpg", quality=93)
    print(f"Rendered {len(IDS)} proposal overlays in {OUT}")


if __name__ == "__main__":
    main()
