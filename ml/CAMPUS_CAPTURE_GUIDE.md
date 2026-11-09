# Campus data capture handoff

The public-data model is a research baseline. A campus dataset is required before evaluating the intended walking-assistance use case. No campus photos or videos have been collected in this workspace yet; the Infinix X6853 is not available through ADB here.

## Capture with the intended phone

1. Obtain campus filming permission and consent where identifiable people may appear. Keep raw media in team-controlled storage, separate from public repositories.
2. Record with the phone's **rear camera at the height and orientation the app will actually use**. Record distinct walks in different locations, lighting, weather, and crowd conditions. Include clear and partially occluded instances of every class.
3. Capture hard negatives as separate scenes: escalators and ramps (not stairs), stools (not chairs), buses and motorcycles (not cars/bicycles), pedestrian crossing or sign posts (not electrical poles), bare pots and vegetation without a pot (not plant pots).
4. For each photo or video, record a unique `scene_id`, `location_code`, `session_id`, date/time, device, lighting/weather, permission/consent status, and whether it contains the seven target classes. A scene is one continuous physical location and capture session; nearby frames share a `scene_id`.
5. Transfer **original** media files, without social-media compression, to a private staging folder. Keep originals unchanged and calculate checksums before annotation. For videos, extract frames at a modest interval and skip near-identical frames.
6. Annotate every visible target object in selected frames using the [frozen seven-class guide](README.md#frozen-seven-class-annotation-guide). Resolve ambiguous examples with a second reviewer. Record exclusions and corrections instead of silently overwriting labels.
7. Split by `scene_id`, location, and capture session **before training**. Keep the independent campus test scenes closed until model choices and confidence thresholds are fixed. Include negative scenes in validation and test.

## Immediate collection priority

Prioritize **electrical poles** and **plant pots in real walkways**, because v3 retains only 98 pole training images and 13 pole public-test images, while plant pots are mostly isolated close-ups. Then collect stairs viewed from both directions, crowded people/chair scenes, parked and moving cars, and bicycles near motorcycles. More frames of the same object do not replace new locations and lighting conditions.

The first field evaluation should report per-class precision/recall, missed obstacles, false alerts per walking minute, detection latency and battery impact on the Infinix X6853, and performance by lighting/occlusion. Walking trials must be supervised until those results are reviewed.
