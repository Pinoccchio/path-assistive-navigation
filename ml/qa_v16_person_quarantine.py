"""Check v16 manifest, ledger, class loss, and exact retained-file identity."""

import json
from collections import Counter

from build_v16_person_quarantine import CLASSES, LEDGER, SOURCE, TARGET, sha256


def main():
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    excluded = ledger["excluded"]
    old = [json.loads(x) for x in (SOURCE / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    new = [json.loads(x) for x in (TARGET / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    expected = [r for r in old if not (r["split"] == "train" and r["source_id"] in excluded)]
    assert new == expected and len(old) - len(new) == 109
    assert Counter(r["split"] for r in new) == Counter({"train": 3186, "val": 251, "test": 620})
    before, after = Counter(), Counter()
    for row in old:
        label = SOURCE / "labels" / row["split"] / f"{row['id']}.txt"
        for line in label.read_text().splitlines():
            if row["split"] == "train":
                before[CLASSES[int(line.split()[0])]] += 1
    for row in new:
        for kind, ext in (("images", ".jpg"), ("labels", ".txt")):
            relative = f"{kind}/{row['split']}/{row['id']}{ext}"
            assert sha256(SOURCE / relative) == sha256(TARGET / relative), relative
        if row["split"] == "train":
            label = TARGET / "labels/train" / f"{row['id']}.txt"
            for line in label.read_text().splitlines():
                after[CLASSES[int(line.split()[0])]] += 1
    lost = before - after
    assert dict(lost) == ledger["lost_labeled_boxes"]
    report = {"retained_pairs_byte_identical": len(new), "removed_train_images": len(excluded),
              "val_test_unchanged": True, "train_boxes_before": dict(before), "train_boxes_after": dict(after),
              "lost_train_boxes": dict(lost),
              "lost_fraction": {key: round(value / before[key], 4) for key, value in lost.items()}}
    (TARGET / "qa_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
