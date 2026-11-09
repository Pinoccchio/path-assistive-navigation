"""Verify v12 differs from v11 only by the two approved train label additions."""

import hashlib
import json

from PIL import Image, ImageDraw

from build_v12_vehicle_label_pilot import LEDGER, SOURCE, TARGET


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(source=SOURCE, target=TARGET, ledger_path=LEDGER):
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    old_rows = [json.loads(line) for line in (source / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    new_rows = [json.loads(line) for line in (target / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(old_rows) == len(new_rows) == 4173
    changed = []
    for old, new in zip(old_rows, new_rows):
        assert {key: value for key, value in old.items() if key != "class_ids"} == {
            key: value for key, value in new.items() if key != "class_ids"}
        split, stem = old["split"], old["id"]
        assert sha256(source / "images" / split / f"{stem}.jpg") == sha256(target / "images" / split / f"{stem}.jpg")
        a = (source / "labels" / split / f"{stem}.txt").read_text(encoding="utf-8").splitlines()
        b = (target / "labels" / split / f"{stem}.txt").read_text(encoding="utf-8").splitlines()
        if a != b:
            assert split == "train" and old["source_id"] in ledger["add_boxes"]
            assert b[:len(a)] == a and len(b) == len(a) + len(ledger["add_boxes"][old["source_id"]]["boxes_xyxy"])
            changed.append(old["source_id"])
        else:
            assert old["class_ids"] == new["class_ids"]
    assert set(changed) == set(ledger["add_boxes"])
    output = target / "correction_review.jpg"
    sheet = Image.new("RGB", (1800, 600), "white")
    draw = ImageDraw.Draw(sheet)
    for i, image_id in enumerate(changed):
        stem = f"oi_v10_train_{image_id}"
        with Image.open(target / "images" / "train" / f"{stem}.jpg") as original_image:
            image = original_image.convert("RGB")
        scale = min(870 / image.width, 540 / image.height)
        rendered = image.resize((round(image.width * scale), round(image.height * scale)))
        x0, y0 = i * 900 + 10, 45
        sheet.paste(rendered, (x0, y0))
        draw.text((x0, 20), f"{image_id}: approved new box in red", fill="black")
        for cls, x1, y1, x2, y2 in ledger["add_boxes"][image_id]["boxes_xyxy"]:
            draw.rectangle((x0 + x1 * scale, y0 + y1 * scale,
                            x0 + x2 * scale, y0 + y2 * scale), outline="red", width=4)
    sheet.save(output, quality=95)
    report = {"source": str(source), "target": str(target), "label_files_changed": len(changed),
              "changed_source_ids": sorted(changed), "image_files_unchanged": len(old_rows),
              "val_test_labels_unchanged": True, "review_image": str(output)}
    (target / "qa_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    verify()
