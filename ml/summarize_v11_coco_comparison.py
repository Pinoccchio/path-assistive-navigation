"""Show paired shared-class matches by public-test source."""

import json
from collections import Counter

from compare_v11_with_coco_pretrained import DATA, OUT


def main():
    report = json.loads(OUT.read_text(encoding="utf-8"))
    manifest = {row["id"]: row for row in
                (json.loads(line) for line in (DATA / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines())
                if row["split"] == "test"}
    output = {}
    for model, result in report["models"].items():
        counts = Counter()
        for row in result["public_test"]["rows"]:
            source = manifest[row["id"]]["source"]
            for name in ("person", "chair", "car", "bicycle", "motorcycle"):
                counts[(source, name, "gt")] += row[f"{name}_gt"]
                counts[(source, name, "matched")] += row[f"{name}_matched"]
                counts[(source, name, "pred")] += row[f"{name}_pred"]
        output[model] = {f"{source}:{name}": {metric: counts[(source, name, metric)]
                                               for metric in ("gt", "matched", "pred")}
                         for source, name, _ in counts}
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
