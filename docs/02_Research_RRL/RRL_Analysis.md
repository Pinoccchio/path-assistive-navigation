# RRL Analysis: Trends and Research Gaps (2021-2026)

This analysis synthesizes results from 10 international studies to support the proposed **Mobile Assistive Navigation Prototype for Visually Impaired Users**.

## 1. Technological Trends
*   **Common use of YOLO-based detection:** Papers #2, #8, and #10 show that YOLO-based models are commonly explored for obstacle detection because they can provide real-time object-detection performance under tested conditions.
*   **Interest in monocular or mobile-compatible distance estimation:** Studies like Paper #3 suggest that camera-based distance or depth estimation may reduce dependence on more expensive sensors, although mobile performance and accuracy must still be tested.
*   **Multi-modal and risk-aware feedback:** Papers #1, #5, and #9 suggest that audio-only feedback can be limited in some situations. Haptic cues and priority-based warning logic may help reduce unnecessary alerts when implemented carefully.

## 2. Identified Research Gaps
*   **Gap 1: Cloud dependency and latency:** Paper #7 (NaviGPT) shows that cloud-based scene reasoning can be limited by network delay for time-sensitive navigation tasks. This supports an offline-first approach for core warning functions.
*   **Gap 2: Small or thin hazard detection:** Paper #8 identifies that thin hazards such as poles or railings can be difficult for standard object-detection models. This supports careful selection of obstacle categories and realistic prototype limitations.
*   **Gap 3: Alert fatigue and prioritization:** Systems that present all detections equally may overwhelm users. Paper #9 (Li et al., 2025) introduces an interaction module that identifies a core obstacle from multiple hazards.
*   **Gap 4: Cognitive load:** Paper #1 suggests that continuous audio feedback can be distracting in some conditions. Haptic feedback may serve as a supplementary warning channel.

## 3. How This Project Addresses the Gaps
The proposed prototype addresses these gaps in a cautious and feasible way by:
1.  **Prioritizing offline-first core warnings:** Keeping camera-based obstacle detection and warning on-device when feasible, while treating internet-dependent features as optional context.
2.  **Using lightweight detection and approximate distance zones:** Evaluating mobile-compatible object detection and distance-zone estimation instead of claiming exact distance measurement.
3.  **Implementing a priority engine:** Selecting a primary feedback candidate from detected objects so the prototype can avoid announcing all detections equally.
