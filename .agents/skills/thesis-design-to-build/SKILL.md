---
name: thesis-design-to-build
description: Develop and verify the Group 8 assistive-navigation thesis Flutter app using its THESIS Figma designs, manuscript, model evidence, and phone QA. Use for this workspace's app planning, Figma inspection/export, implementation, and research-aligned evaluation.
---

# Thesis design to build

Use in the assistive-navigation THESIS workspace. This adapts Kuwenturo's source-to-build process to Flutter and an offline research prototype; Kuwenturo node IDs, assets, product behavior, and backend architecture do not belong here.

## Start from current evidence

Read `README.md`, `TEAM_START_HERE.md`, and `apps/mobile/README.md`. For feature scope read `docs/05_Product/Assistive_Navigation_PRD.md` and the relevant sections of `docs/04_Manuscript/Assistive_Navigation_Thesis_Ch1_Ch3.md`. Inspect the current app and `apps/mobile/assets/model/model_metadata.json` before describing capabilities. Older PRD current-state passages and seven-class descriptions predate the Flutter eight-class prototype; do not undo current code to match them. If evidence conflicts, identify the conflict and follow the user's accepted scope.

The current structure is Flutter under `apps/mobile/`, ML/data tooling under `ml/`, historical experiments under `runs/` and `notebooks/`, and research documents under `docs/`. Check for a Git root before using Git; this workspace may not be a repository. Preserve unrelated work and recorded results.

## Choose the relevant workflow

- For Figma inspection, asset exports, source fidelity, or UI implementation, read [references/figma-workflow.md](references/figma-workflow.md).
- For detector, dataset, feedback, accessibility, or phone evaluation changes, read [references/research-and-device.md](references/research-and-device.md).
- For manuscript, PDF, or defense artifacts, apply the corresponding available document/PDF/presentation skill and verify claims against current evidence. Read both DOCX/PDF when comparing supplied requirements; do not assume identical content.

## Connect source to implementation

For the requested feature, connect document requirement, Figma frame/layer/comment, current code, and observed behavior. Use a concise screen/feature inventory in `docs/05_Product/` when it materially helps a multi-screen task: source node/version, target behavior, implemented state, conflicts, and QA evidence. Update an existing ledger rather than creating a report for every small change.

Inspect actual artwork before recreating it. Export reusable source assets when needed; implement text, controls, layout, and semantics natively in Flutter. Preserve the user's accepted camera-preview layout and existing behavior unless the request changes them. A Figma mockup is not proof that GPS, distance, speech, haptics, or alert prioritization works.

Use available Flutter performance guidance when changing runtime-sensitive camera/inference code. Keep camera/model work bounded, prevent overlapping frame processing, and handle Stop, permission failure, and app lifecycle consistently. Native platform migration is a PRD option, not an automatic requirement for every edit.

## Verify and hand back

Run checks proportional to the change: focused Dart formatting/analyzer checks, relevant existing Flutter tests, and meaningful new tests for transforms or state behavior when needed. Do not regenerate golden files merely to make a failure pass. Compare actual rendering with Figma at source dimensions and the target phone size, including large text and TalkBack when relevant. Desktop render checks cannot prove phone camera correctness or accessibility.

The user runs `flutter run` themselves. Do not launch it, install a build, or start a debug session on their phone unless explicitly requested. Give exact manual steps when phone verification is needed; leave those results marked pending until observed.

Report what changed, checks actually performed, and remaining gaps. Keep design target, implemented code, desktop-tested behavior, physical-device evidence, trained model results, and released state distinct. Continue within authorized scope; this skill adds no standing permission to edit Figma, retrain models, reset data, publish, deploy, or release.
