"""Create a local display gallery from frozen public test images for phone QA."""

import html
import json
import shutil
from pathlib import Path

from PIL import Image

from phase1 import ROOT

DATA = ROOT / "data/processed/public_phase1_person_retention_candidate"
OUT = ROOT / "qa/phone_test_gallery"
NAMES = ("person", "chair", "stairs", "car", "bicycle", "electrical_pole",
         "plant_pot", "motorcycle")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    paired = json.loads((ROOT / "runs/public_phase1_person_retention_candidate/paired_public_diagnostic_512.json").read_text(encoding="utf-8"))
    matched = {name: {row["id"] for row in paired["public_test"]["rows"]
                      if row[f"{name}_matched"] > 0}
               for name in ("person", "chair", "car", "bicycle", "motorcycle")}
    stairs = json.loads((ROOT / "runs/public_phase1_person_retention_candidate/stair_public_diagnostic_512.json").read_text(encoding="utf-8"))
    matched["stairs"] = {row["id"] for row in stairs["candidate"]["rows"] if row["matched"] > 0}
    selected = []
    for cls, name in enumerate(NAMES):
        candidates = []
        for label in (DATA / "labels/test").glob("*.txt"):
            boxes = []
            for line in label.read_text(encoding="utf-8").splitlines():
                parts = line.split()
                if int(parts[0]) == cls:
                    boxes.append(tuple(map(float, parts[1:5])))
            if not boxes:
                continue
            area = max(w * h for _, _, w, h in boxes)
            if area > 0.55 or area < 0.06:
                continue
            known_match = label.stem in matched.get(name, set())
            score = (1 if known_match else 0, -abs(area - 0.22))
            candidates.append((score, label.stem, len(boxes)))
        if not candidates:
            raise SystemExit(f"No frozen-test image for {name}")
        _, image_id, count = max(candidates)
        source = DATA / "images/test" / f"{image_id}.jpg"
        target = OUT / f"{cls + 1:02d}_{name}.jpg"
        with Image.open(source) as image:
            image.convert("RGB").save(target, quality=90)
        selected.append({"label": name, "image": target.name,
                         "source_id": image_id, "labeled_boxes": count})
    (OUT / "manifest.json").write_text(json.dumps(selected, indent=2), encoding="utf-8")
    slides = "\n".join(
        f'<section><h2>{html.escape(item["label"].replace("_", " ").title())}</h2>'
        f'<img src="{html.escape(item["image"])}" alt="{html.escape(item["label"])} test image">'
        f'<p>Expected label: {html.escape(item["label"])} · Public test image {index}/8</p></section>'
        for index, item in enumerate(selected, 1))
    page = f"""<!doctype html><html lang="en"><meta charset="utf-8">
<title>Phone detection test gallery</title>
<style>body{{margin:0;background:#111;color:white;font:24px system-ui;text-align:center}}
section{{display:none;height:100vh;box-sizing:border-box;padding:10px}}
section.active{{display:flex;flex-direction:column;align-items:center;justify-content:center}}
h2,p{{margin:8px}}img{{max-height:75vh;max-width:95vw;object-fit:contain}}
aside{{position:fixed;right:12px;top:12px;font-size:14px;background:#222;padding:8px}}</style>
<aside>← → switch image · Space auto-play</aside>{slides}
<script>const slides=[...document.querySelectorAll('section')];let index=0,timer;
function show(n){{slides[index].classList.remove('active');index=(n+slides.length)%slides.length;
slides[index].classList.add('active')}}show(0);
document.addEventListener('keydown',e=>{{if(e.key==='ArrowRight')show(index+1);
if(e.key==='ArrowLeft')show(index-1);if(e.code==='Space'){{e.preventDefault();
if(timer){{clearInterval(timer);timer=null}}else timer=setInterval(()=>show(index+1),5000)}}}});</script></html>"""
    (OUT / "index.html").write_text(page, encoding="utf-8")
    print(OUT / "index.html")


if __name__ == "__main__":
    main()
