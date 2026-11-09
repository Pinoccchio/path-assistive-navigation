# Presentation Insights: 10 Slides for Monday's Defense

Use the following content for your PPT slides. Each slide is aligned with your RRL findings (2021–2026).

---

## Slide 1: Title & Overview
**Topic:** Development and Evaluation of an Offline Mobile-Based Obstacle Detection and Distance Estimation System.
**Presenter:** Group 8 - Assistive Navigation for Visually Impaired.
**Goal:** Identifying and bridging research gaps in global assistive technology.

## Slide 2: RRL Scope & Methodology (2021–2026)
*   **Studies Reviewed:** 10 International peer-reviewed papers.
*   **Timeframe:** 2021–2026 (Focus on the latest AI advancements).
*   **Key Repositories:** Nature Scientific Reports, IEEE Xplore, MDPI Sensors, ACM DL.
*   **Focus:** YOLO architectures, Depth Estimation, and Multi-modal Feedback.

## Slide 3: Global Trend 1: Real-Time AI Vision (YOLO)
*   **Finding:** YOLO (v8 and v10) is the benchmark for object detection in 2024–2025.
*   **Validation:** Paper #2 and #8 show higher mAP scores for navigation hazards than previous models.
*   **Application:** We leverage YOLOv8 to ensure fast (real-time) detection on mobile.

## Slide 4: Global Trend 2: Low-Cost Spatial Sensing (MiDaS)
*   **Finding:** Monocular depth estimation (AI-based) is replacing expensive LiDAR sensors.
*   **Validation:** Paper #3 proves that AI-calculated distance is safe for walking-speed navigation.
*   **Application:** Our system uses MiDaS for 100% software-based distance estimation.

## Slide 5: Research Gap: The "Cloud Latency" Problem
*   **Issue:** Cloud-based models like GPT-4 (Paper #7) have 2-5 second delays.
*   **Critical Risk:** A 2-second delay means a user might walk into a hazard before hearing the alert.
*   **Our Solution:** 100% Offline operation for sub-25ms response times.

## Slide 6: Research Gap: The "Alert Fatigue" Problem
*   **Issue:** Standard systems treat all obstacles equally, causing information overload (Paper #9).
*   **Finding:** Li et al. (2025) validates that identifying a **"core obstacle"** reduces cognitive tunneling.
*   **Our Solution:** A Priority Engine that ranks hazards and filters non-hazardous feedback.

## Slide 7: Technical Proof 1: Advanced Haptic Feedback
*   **Highlight:** Paper #1 (Nature, 2024) proves haptic feedback can reach parity with sighted vision.
*   **Result:** Participants navigated complex office buildings without any audio cues using only haptics.
*   **Validation:** Supports our use of vibration zones for obstacle distance.

## Slide 8: Technical Proof 2: Collision Avoidance Accuracy
*   **Highlight:** Paper #5 (Nature Communications, 2025) achieved **100% collision avoidance** through cross-modal learning.
*   **Finding:** AI systems out-perform white canes (26% avoidance) for sudden-appearance obstacles.
*   **Validation:** Proves AI navigation is technically safer than traditional tools.

## Slide 9: User-Centric Design Gaps (User Feedback)
*   **Highlight:** Paper #4 and #10 identify "computational load" and "usability" as key barriers.
*   **Finding:** If the phone gets too hot or the battery drains in 30 mins, users won't use it.
*   **Our Focus:** Optimizing TFLite models for efficient, long-lasting mobile deployment.

## Slide 10: Conclusion & Readiness for Defense
*   **Summary:** Our system is not just an app; it is a solution built to fill global gaps in offline speed and multimodal safety.
*   **Outcome:** All 10 studies validate our choice of YOLOv8, MiDaS, and Haptic feedback as the "Gold Standard" for 2026.
*   **Ready for Implementation.**
