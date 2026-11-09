# Public obstacle-label policy (v4-v9 candidates)

This policy is for dataset curation of the seven existing YOLO classes. It describes image labels, not app safety or an approved navigation taxonomy. Each candidate applies only corrections supported by its visual review ledger; other classes and unreviewed images remain provisional.

| Class | Include | Exclude / quarantine | Box convention |
| --- | --- | --- | --- |
| `person` | Visible human body, including partial body | Pictures of people on signs/screens | Tight box around visible body |
| `chair` | Freestanding seat with back | Backless stool unless class is broadened later | One box per chair |
| `stairs` | Fixed, walkable staircase or group of steps | Ladder, escalator, decorative step pattern | One box around each contiguous staircase flight; separate flights may have separate boxes |
| `car` | Passenger automobile | Bus, truck, motorcycle, scooter | One box per vehicle |
| `bicycle` | Pedal bicycle | Motorcycle and scooter | One box per bicycle |
| `electrical_pole` | Utility or electrical-service support pole | Pedestrian crossing-button post, streetlight-only post, building column, sign-only post | One vertical box per pole; crop at image edge if partly visible |
| `plant_pot` | Container with a living plant rooted in it | Empty pot, soil-only pot, cut flowers in a vase | Box the physical container, including attached base; foliage is not part of this box |
| `motorcycle` (v8 only) | Motorcycle, motor scooter, motor trike | Pedal bicycle | One box per powered vehicle; this auxiliary class is for model discrimination and is not an app alert class |

**Uncertainty rule:** Quarantine the full image from a candidate split when a label's object identity or stair box granularity cannot be resolved from the available review. Do not silently turn uncertain positives into negatives. A corrected image can retain its other valid class boxes. Record exact line removals and image quarantines in the candidate build report.

The rule for `stairs` is a proposed consistent target for walking assistance. Existing source data often uses per-step boxes; the v4-v6 builder quarantined images with three or more stair boxes for later manual relabeling. Images with one or two stair boxes can still have geometry problems and are not certified by that screen. The pole test set is small, so per-class performance remains highly uncertain after corrections. Future phone/campus data should be collected and annotated under this same policy once that work resumes.

The v8 candidate adds the auxiliary `motorcycle` class only for boxes visually reclassified from the v6 bicycle labels. It quarantines one train image with a clearly overlarge stair box. The resulting motorcycle labels are still a small and clustered sample; source-separated evaluation is required before claiming a robust vehicle distinction.

The v9 candidate adds 300 COCO train2017 images selected before its training run. COCO `person`, `chair`, `car`, `bicycle`, and `motorcycle` boxes map to the corresponding project classes. COCO images with a `potted plant` label are excluded because that box convention includes foliage and conflicts with the container-only `plant_pot` policy. Existing validation and test images are unchanged. COCO image licenses are per-image and must be checked before redistribution.
