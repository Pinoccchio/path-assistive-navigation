"""Verify v15 removes only approved train images and copies all remaining data."""

import json
from collections import Counter

from build_v15_oi_quarantine import LEDGER, SOURCE, TARGET, sha256


def main():
    excluded = set(json.loads(LEDGER.read_text(encoding="utf-8"))["excluded"])
    old_rows = [json.loads(line) for line in (SOURCE / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    new_rows = [json.loads(line) for line in (TARGET / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    expected = [row for row in old_rows if not (row["split"] == "train" and row["source"] == "OpenImagesV7"
                                                  and row["source_id"] in excluded)]
    assert new_rows == expected and len(new_rows) == len(old_rows) - len(excluded)
    assert Counter(row["split"] for row in new_rows) == Counter({"train": 3295, "val": 251, "test": 620})
    for row in new_rows:
        split, stem = row["split"], row["id"]
        for kind, ext in (("images", ".jpg"), ("labels", ".txt")):
            relative = f"{kind}/{split}/{stem}{ext}"
            assert sha256(SOURCE / relative) == sha256(TARGET / relative)
    report = {"quarantined_train_ids": sorted(excluded), "remaining_files_unchanged": len(new_rows),
              "train_count": 3295, "val_test_unchanged": True}
    (TARGET / "qa_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
