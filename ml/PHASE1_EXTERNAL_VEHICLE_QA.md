# External public-image vehicle QA — 2026-09-29

The frozen v6 and v7 detectors were evaluated at confidence 0.25 and image size 512 on the **same 80 COCO val2017 images**: 40 with bicycle annotations and no motorcycle annotation, and 40 with motorcycle annotations and no bicycle annotation. Images were selected with seed `20260929` before inference. The [selection manifest](../data/source/coco_external/selection.json) records image IDs, boxes, and SHA-256 digests. Its annotation file matched the published SHA-256 `e8c7f7908f1d7278341fae127d0da654f102f11bd7b21d8aeefa635b8c810b6f`. No selected image was an exact-byte match for a v7 project image. These are public images; they do not substitute for an untouched local/phone test. COCO val may also be familiar to model-development ecosystems, so this is an external *project-data* check rather than a claim of model-development independence.

| Detector | Bicycle boxes matched at IoU ≥ 0.5 | Recall on 98 bicycle boxes | Precision on bicycle predictions | Motorcycle-only images with any bicycle prediction |
| --- | ---: | ---: | ---: | ---: |
| [v6](../data/source/coco_external/v6_external_vehicle_qa.json) | 26 | 0.265 | 0.441 | 13/40 |
| [v7](../data/source/coco_external/v7_external_vehicle_qa.json) | 21 | 0.214 | 0.368 | 6/40 |

The v7 correction reduced motorcycle-as-bicycle image false alarms on this new slice, but bicycle recall and precision **fell**. The v7 model is not ready as a walking-assistance detector. Of the 98 bicycle boxes, 25 have area below 32×32 pixels and 53 below 64×64 pixels at source resolution; small objects contribute to difficulty, but that does not excuse the misses. All six v7 motorcycle-only false-alarm images were visually checked and show motorcycles, not pedal bicycles. The [QA script](coco_vehicle_external_qa.py) computes one-to-one IoU matching; its metrics are specific to this selected slice, confidence, image size, and bicycle class, not a COCO-wide mAP.

The stair contact-sheet review found that two initially suspicious Open Images cases were **valid**: `openimagesv7_test_313f51fc7ef2a042` boxes the fixed steps below ladders, and `openimagesv7_validation_f9e61241218288ba` boxes stairs behind a train. Their labels must stay. One train image, `openimagesv7_train_b11a9ac6faa28d32`, has a stair box covering most of a person and the landing; it needs box relabeling or image quarantine in the next curated candidate. Existing v7 data and checkpoint were left immutable, and no metric is claimed from a silent test-label change.

The training response was an audited eight-class candidate with an explicit motorcycle label and a second frozen COCO holdout. Additional source-diverse bicycle/motorcycle training images and a separate future test remain necessary. Stair boxes require a geometry review and correction ledger. Re-evaluate the exported TFLite detector after a candidate passes image-level QA, then run detection and latency QA on the Infinix X6853. Campus collection remains deferred as requested.

An eight-class candidate and a second frozen holdout were subsequently completed; see [v8 status](PHASE1_V8_STATUS.md). The first 80-image slice above became development evidence and was not used for v8 training.

COCO source: [COCO API](https://github.com/cocodataset/cocoapi); [annotation mirror and checksum](https://huggingface.co/datasets/LibreYOLO/coco2017). Image rights vary by source image; keep image IDs and original license metadata if redistributing.
