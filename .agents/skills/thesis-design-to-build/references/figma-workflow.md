# THESIS Figma inspection and export

## Source and access

File: `https://www.figma.com/design/aFXQm7eAu32gXNeWt7WJVe/THESIS`.

REST access was verified on 2026-11-09 using the existing local Figma token configured in `C:/Users/User/Documents/first_year_files/folder_for_jobs/KUWENTURO/kuwenturo/.env.local`, key `FIGMA_ACCESS_TOKEN`. Read only that value into process memory when reusing this authorized setup; do not print/copy the environment file or expose unrelated credentials. Always use the THESIS file key `aFXQm7eAu32gXNeWt7WJVe`, never the Kuwenturo `FIGMA_FILE_KEY`. If a thesis-specific private configuration exists later, prefer it. Do not put tokens in this skill, source, public assets, raw exports, or screenshots. No standalone Figma CLI is required: the established workflow uses REST scripts.

Existing local source snapshot: `qa/figma-source/file.json` and `comments.json`. These contain design data, not credentials. Refresh live sources before relying on them for implementation. They are reference material, not assets to bundle into the app.

## Source map (verify before reuse)

Page `0:1`, Page 1. Snapshot version `2419075896925554276`, last modified `2026-11-09T15:44:59Z`:

| Node | Source | Dimensions |
| --- | --- | --- |
| `2:1624` | Navigation HUD | 390 x 844 |
| `2:1669` | Settings and accessibility | 390 x 844 |
| `2:1734` | Hazard log and GPS context | 390 x 844 |
| `2:1787` | PATH design system and accessibility reference | 1440 x 3748 |

All four frame trees were retrieved. Comments endpoint returned zero comments at that check; never assume the file will remain comment-free. Three app frames plus a reference board do not mean four product screens.

## Read and export using REST

Use `X-Figma-Token` in the request header; never put it in a URL or log. The requests below are relative to `https://api.figma.com/v1/`:

1. `GET files/:file_key?depth=1`: page outline, version, lastModified. `GET files/:file_key/comments`: behavioral notes. Preserve author, date, replies, resolution status, and node location when available.
2. `GET files/:file_key/nodes?ids=:node_ids`: inspect requested page/frame trees, children, visibility, text/style overrides, fills, strokes, bounds, clipping, and transforms. A full `GET files/:file_key` is feasible for this small file; switch to scoped nodes if it grows or times out.
3. `GET images/:file_key?ids=:node_ids&format=png&scale=1`: source-size frame reference renders. Use SVG or higher-scale PNG for individual reusable vector/group assets as appropriate.
4. `GET files/:file_key/images`: original image-fill URLs, keyed by imageRef. Match the ref to its layer and preserve crop/scale/transform intent. Render URLs are temporary; download the intended files rather than hotlinking them.

Keep raw JSON, full-screen references, render URL caches, and source manifests under `qa/figma-source/` or another clearly separated private/reference directory. Keep only used runtime artwork under `apps/mobile/assets/` and register it in `pubspec.yaml`. If Git is introduced, ignore credentials and raw/cache exports before staging; review rights and scope before publishing any design data.

For each used asset record node ID/imageRef, file version, exported path, dimensions, and relevant bounds. Check HTTP success, decode downloaded images, verify nonempty content and inspect the actual render. For a requested bulk pack, provide a visual index and source manifest; do not download the whole pack merely to answer a metadata question. Use bounded batches, respect rate-limit responses, and do not loop indefinitely on errors.

## Fidelity and accessibility

The reference board specifies OLED black, yellow `#FFD700` actions, Inter typography with Roboto fallback, 64dp targets, 16dp target separation, redundant severity text/shapes, local settings, 200% font scaling, and explicit TalkBack traversal/announcements. Read the actual layer text for full specifications instead of relying on this synopsis. Distinguish design contrast intent from measured contrast and accessibility certification.

Export actual icons/illustrations where reusable. Do not replace available source art with emoji or approximate drawings, and do not use a full-screen screenshot as the Flutter interface. Native layout shapes and controls are appropriate when the source defines ordinary tokens/geometry. Separate static example labels from live model outputs. Preserve full mixed text styling when it applies, clipping/masks, and image crop origins; compare painted bounds as well as layout bounds when aligning assets or hit targets.

Compare all relevant dimensions: typography, spacing, colors, proportions, camera placement, safe areas, artwork, large text, semantics, and interactive states. Test the full visible hit area of each control, not only its label. Include permission/model/loading errors, Start/Stop, settings persistence, navigation/back, unavailable features, and lifecycle transitions relevant to the requested change.

Use the user's existing authenticated Figma browser only when visual inspection requires it; apply the available browser navigation skill, discover the current exact tab, and preserve tabs/login. Restore and verify any viewport emulation afterward. Do not edit designs or post comments unless requested.

## Known design/implementation differences

The Figma mockups show exact meters, danger/caution/safe states, GPS lock/address, battery percentage, speech/haptics, and log events. These are design examples, not observed device results. The design's distance thresholds are illustrative until calibrated and evaluated under the thesis protocol. Do not use an object box or relative MiDaS output to fabricate meters. Do not show fixed GPS/battery/sample events as live telemetry. Any disabled preview must be clearly labeled; implement source-supported features only within the requested and validated scope.
