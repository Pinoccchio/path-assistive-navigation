# Topic 6 — Assistive Navigation for Visually Impaired

**SDG 10: Reduced Inequalities**

## Table of Contents

**Part A — Thesis Proposal (what we submit)**
1. [Title, Overview, SDG Alignment, CS Domain](#proposal)
2. [CV vs AR Clarification](#important-clarification-computer-vision-not-ar) — panel specifically asked for this
3. [Key Terms Explained](#what-is-multi-modal-feedback-key-terms-explained) — haptic, TTS, priority engine, zones
4. [Key Technologies](#key-technologies) — YOLOv8n, MiDaS, TFLite, Flutter
5. [Research Gap](#research-gap) — 5 documented gaps with citations
6. [Dataset](#dataset) — COCO, Open Images, custom campus data

**Part B — System Design**
7. [Our Goal](#our-goal-what-were-trying-to-achieve) — big picture, step-by-step goals, success metrics
8. [System Architecture](#system-architecture) — full pipeline diagram
9. [Key Novel Features](#key-novel-features-what-makes-this-different) — what makes this different
10. [Differentiation from Existing Apps](#differentiation-from-existing-solutions) — comparison table

**Part C — Methodology & Evaluation**
11. [24-Week Timeline](#methodology-24-week-timeline)
12. [Evaluation Plan](#evaluation-plan) — technical metrics, user metrics, variables

**Part D — Defense & Feasibility**
13. [Panel Defense Q&A](#panel-defense-preparation) — 8 likely questions with answers
14. [Key Literature References](#key-literature-references) — 8 core + 25+ extended papers organized by gap
15. [Technical Feasibility Verification](#technical-feasibility-verification) — all components confirmed
16. [Feasibility Analysis](#feasibility-analysis-can-we-actually-build-this) — offline proof, gap-by-gap analysis, limitations
17. [Why Zone-Based Distance Works](#why-zone-based-distance-works-even-without-centimeter-accuracy) — camera limitations explained, why zones > exact numbers
18. [References (APA 7)](#references-apa-7-format) — full APA 7 citations with DOI/URL links for all papers

---

## Proposal

### Title

> Development and Evaluation of an Offline Mobile-Based Obstacle Detection and Distance Estimation System with Multi-Modal Feedback for Visually Impaired Navigation

### Overview

Over 2.2 billion people globally experience vision impairment (WHO, 2023), yet existing assistive navigation tools remain critically limited: they identify objects but cannot estimate distance, depend on cloud connectivity, deliver audio-only feedback without haptic (vibration-based) reinforcement, treat all obstacles with equal priority regardless of danger, and offer no personalization. This study develops and evaluates a **computer vision-based** mobile assistive navigation system that integrates real-time object detection (YOLOv8n) with monocular depth estimation (MiDaS v2.1 Small) — both running **entirely on-device** via TensorFlow Lite — to provide visually impaired users with intelligent, multi-modal navigation assistance. The system processes live camera frames to detect navigation-relevant obstacles (person, chair, table, door, stairs, car, bicycle, couch, bottle, backpack), estimates the distance to each detected object, classifies threats into danger zones (DANGER < 1m, CAUTION 1–3m, SAFE > 3m), and delivers feedback through two channels: **audio** (text-to-speech that speaks directional cues like "Chair, 2 meters, to your left") and **haptic** (the phone vibrates in patterns scaled to how close the obstacle is — stronger vibrations for closer objects). A priority engine ensures the most dangerous and closest objects are announced first, preventing information overload. User preferences allow customization of alert thresholds, feedback modes, object filters, and speech parameters. The system is built with Flutter for cross-platform deployment and evaluated through both technical benchmarks (mAP, FPS, distance MAE) and a user study (SUS questionnaire, task completion rate, collision count) with visually impaired participants.

### SDG Alignment

Addresses **SDG 10 (Reduced Inequalities)**, specifically Target 10.2: "empower and promote the social, economic, and political inclusion of all, irrespective of age, sex, disability, race, ethnicity, origin, religion, or economic or other status." The system directly reduces mobility barriers for visually impaired individuals by providing free, offline, smartphone-based navigation assistance — eliminating the need for expensive specialized hardware (e.g., WeWALK at $850–1,150) and ensuring accessibility regardless of internet connectivity or economic status.

Additionally supports **SDG 3 (Good Health and Well-Being)** by reducing the risk of injury from undetected obstacles during independent navigation.

### CS Domain

Computer Vision · Mobile Computing · Assistive Technology · Human-Computer Interaction

### Important Clarification: Computer Vision, NOT AR

> **This was specifically asked by the panel.** This proposal uses Computer Vision, NOT Augmented Reality.

| Aspect | Augmented Reality (AR) | Computer Vision (CV) — Our Approach |
|---|---|---|
| **What it does** | Puts visual overlays on the screen (like Pokemon Go) | AI analyzes camera frames to understand surroundings |
| **Output** | Visual overlays on screen | Voice (TTS) + vibration — **no screen needed** |
| **Requires seeing screen?** | Yes | **No** |
| **Useful for blind users?** | No — users cannot see overlays | **Yes — feedback through non-visual channels** |
| **Camera role** | Display with overlays | **Input sensor for AI processing** |
| **Examples** | Pokemon Go, IKEA Place | **Object detection, depth estimation** |

The camera serves as an **input sensor** — the AI processes what the camera sees and communicates it through voice and vibration. At no point does the system require the user to look at the screen.

---

### What is "Multi-Modal Feedback"? (Key Terms Explained)

Before diving into the technical details, here are the key terms used throughout this proposal:

- **Haptic feedback** = feedback through **touch and vibration**. When your phone buzzes for a notification, that is haptic feedback. In this system, the phone vibrates in different patterns to tell the user how close an obstacle is — strong, rapid vibrations mean "danger, very close" while a gentle single pulse means "something is nearby but far away." This is useful because the user can *feel* the warnings even in noisy environments where they might miss audio.

- **Multi-modal feedback** = using **more than one sense** to communicate information. Instead of only speaking to the user (audio), the app also vibrates the phone (haptic/touch). Using two senses together — hearing AND touch — has been shown in research to be more effective than either one alone.

- **TTS (Text-to-Speech)** = the phone reads text aloud. For example, the app converts the message "Chair, 2 meters, to your left" into spoken words that the user hears through the phone speaker or earphones.

- **Priority engine** = the app's decision-making system that determines **which obstacle to warn about first**. Instead of announcing everything at once ("chair, table, person, door, bottle..."), it ranks obstacles by danger level and distance, then announces the most critical one first (e.g., stairs 1 meter ahead gets announced before a chair 3 meters to the right).

- **Zone-based alerts** = instead of saying exact distances (which can be confusing), the system groups obstacles into three simple zones:
  - **DANGER (red zone)** = object is less than 1 meter away → phone vibrates strongly 3 times + urgent voice alert
  - **CAUTION (yellow zone)** = object is 1 to 3 meters away → phone vibrates moderately 2 times + normal voice alert
  - **SAFE (green zone)** = object is more than 3 meters away → phone vibrates gently 1 time + soft voice alert (or no alert, depending on user preference)

---

### Key Technologies

| Category | Details |
|---|---|
| Object Detection | YOLOv8n (Nano) — anchor-free architecture, ~3.2M parameters, pre-trained on COCO, fine-tuned to ~10 navigation-relevant classes |
| Depth Estimation | MiDaS v2.1 Small — pre-trained monocular depth estimation model with official TFLite support |
| On-Device Inference | TensorFlow Lite (INT8 quantized) — fully offline, no cloud dependency |
| App Framework | Flutter (cross-platform Android/iOS) with `tflite_flutter`, `camera`, `flutter_tts`, `vibration` packages |
| Post-Processing | Custom priority engine (ranks obstacles by danger × closeness), zone classification (DANGER/CAUTION/SAFE), directional mapping (LEFT/CENTER/RIGHT) |
| Training Environment | Python, Ultralytics YOLOv8, Google Colab (free T4 GPU) |
| Evaluation Metrics | mAP@0.5, FPS, inference latency (ms), distance MAE (meters), model size (MB), battery consumption, SUS score, task completion rate, collision count |

### Research Gap

While commercial assistive applications like Google Lookout and Seeing AI provide basic scene description, they suffer from critical limitations documented in recent peer-reviewed literature:

1. **No distance estimation** — existing smartphone-based systems identify objects but cannot determine how far they are from the user. DeepNAVI (2022) explicitly states: *"smartphones do not provide depth information, cannot determine distance from user to obstacle,"* forcing users to navigate without spatial awareness. This gap persists in recent work: YOLO-OD (MDPI Sensors, 2024) and PC-CS-YOLO (MDPI Sensors, 2025) achieve real-time detection at 20.6ms but include *no distance estimation component*. A YOLOv8 Android study (Procedia Computer Science, 2025) achieves mAP50=79.9% but provides *no distance feedback*. While recent wearable systems like Li et al. (MDPI Electronics, 2025) utilize RGB-D cameras for core obstacle distance, most smartphone-only solutions remain limited. The Shape-Changing Haptic Interface study (Nature Scientific Reports, 2024) indicates direction but *not obstacle distance*. A Real-Time Assistive Navigation system (arXiv:2504.20976, 2025) demonstrates that reduced MAE is achievable with on-device depth estimation, validating our MiDaS-based approach.

2. **Cloud dependency** — most systems require internet connectivity for inference, rendering them unusable in areas with poor connectivity. NaviSense (ACM SIGACCESS, 2024) acknowledges *"reliance on cloud-based models, raising privacy and connectivity concerns"* as a fundamental limitation. PathFinder (CHI 2023) explicitly identifies this gap: *"Unlike existing assistive tools that often rely on online services or APIs making them costly and internet-dependent, PathFinder addresses these limitations as a fully offline system."* Elmannai & Elleithy (MDPI Sensors, 2024 update) confirm that *"cloud-based systems restricted their use in areas with patchy internet."* NaviGPT (arXiv:2410.04005, 2024) exemplifies the problem — it requires the GPT-4 API plus Apple Maps API, making it entirely cloud-dependent by design and inaccessible without internet.

3. **No priority-based alerts** — current systems announce all detected objects with equal urgency, overwhelming users with information. Multiple systematic reviews identify priority-based intelligent alerts as critical future work, yet virtually no existing system implements danger-weighted prioritization. Across all YOLO-based papers surveyed (YOLO-OD, PC-CS-YOLO, TFP-YOLO, YOLO-Extreme, 2024–2025), *all obstacles are treated equally in feedback* with *no hierarchy of obstacle warnings*. The Neurocomputing survey (2024, Vol. 606, 128284) warns that *"excessive or incorrect information frequently causes confusion and reduces trust"* — directly supporting the need for priority filtering. Only one recent system found — Li et al. (2025) — implements an "intelligent interaction module" to identify a "core obstacle" from multiple hazards, but risk-based prioritization for smartphone-based apps remains an unaddressed frontier. **This is the most under-addressed gap in the literature.**

4. **Audio-only feedback, no vibration alerts** — the majority of assistive navigation systems rely exclusively on spoken audio output. They do not use the phone's vibration motor to provide touch-based (haptic) warnings. A systematic literature review of 132 papers (ACM Transactions on Accessible Computing, 2025) found that for white cane users, *"auditory feedback results in a 22 times higher cognitive load than haptic feedback"* — a striking statistic proving audio-only is cognitively inferior. A scoping review of 28 articles (Journal of Visual Impairment & Blindness, 2025) recommends a *"multimodal feedback approach with audio"* and identifies *"hands-free vs hand-held gaps"* as critical. The NYU Tandon VR Navigation Study (JMIR Rehabilitation, 2024) with 72 participants found that *"voice feedback is not efficient in noisy environments"* and that *"haptic is language-independent"* with *"no information privacy problem."* The Shape-Changing Haptic Interface study (Nature Scientific Reports, 2024) demonstrated that haptic feedback achieved **parity with natural sighted vision** for navigation tasks. Most powerfully, a wearable obstacle avoidance system (Nature Communications, 2025, Vol. 16, 2857) using cross-modal learning achieved **100% collision avoidance rate** (compared to white cane's 26% for suddenly appearing obstacles), with latency <320ms and ~11 hours battery life — demonstrating that multi-modal systems dramatically outperform single-modality approaches.

5. **No personalization** — users cannot customize detection preferences, alert thresholds, or feedback modes. AI Wearable Vision (ArXiv, 2024) identifies that *"personalization is almost entirely missing in current systems,"* despite diverse user needs and preferences. The Neurocomputing survey (2024) confirms that *"customization and user flexibility are frequently ignored"* with *"numerous assistive solutions adopting a uniform approach and neglecting the varied needs of users."* The ACM Transactions on Accessible Computing review (2024) acknowledges that *"the needs for blind users are very different"* and that *"learning systems enable customization based on individual tastes, language proficiency and specific task needs."* AI-Powered Assistive Technologies (arXiv:2503.15494, 2025) identifies personalization as future work, not current capability. A User-Centered Insights study (arXiv:2504.06379, 2024) surveying 19 participants found that *"adoption remains limited due to usability challenges, financial constraints, and lack of alignment with user needs."* Smart Wearable Mobility Aids reviews (2024–2025) consistently report *"personalization mechanisms incomplete"* and *"user preference learning absent."* Special focus on **SnapStick (2025)** which highlights the importance of VLM integration for personalized spatial reasoning.

---

### Dataset

| Source | Description |
|---|---|
| [MS COCO 2017 (cocodataset.org)](https://cocodataset.org/) | 118K training + 5K validation images with 80 object classes; filtered to ~10 navigation-relevant classes (person, chair, table, door, couch, bicycle, car, bottle, backpack, potted plant) |
| [Open Images V7 (storage.googleapis.com)](https://storage.googleapis.com/openimages/web/index.html) | Supplementary dataset for classes underrepresented in COCO (stairs, curb, pole); used as needed to augment training data |
| Custom Campus Dataset (self-collected) | 200–500 annotated images of the local campus environment for real-world evaluation; annotated using Roboflow; ensures the system is tested against realistic navigation scenarios |

---

### Our Goal (What We're Trying to Achieve)

#### The Big Picture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         TOPIC 6 GOAL                                    │
│                                                                         │
│   Build a WORKING assistive navigation app for visually impaired        │
│   users that detects obstacles, estimates distance, and provides        │
│   intelligent voice + vibration feedback — ALL OFFLINE on a smartphone  │
└─────────────────────────────────────────────────────────────────────────┘
```

#### Step-by-Step Goals

| Step | Goal | What We Do |
|------|------|------------|
| 1 | **Prepare detection model** | Fine-tune YOLOv8n on COCO (filtered to ~10 classes), export to TFLite (INT8 quantized) |
| 2 | **Integrate depth estimation** | Use pre-trained MiDaS v2.1 Small TFLite model for monocular depth estimation |
| 3 | **Build the app** | Flutter app with camera pipeline → TFLite inference → post-processing → output |
| 4 | **Implement priority engine** | Rank detected objects by (danger_level × proximity), announce most critical first |
| 5 | **Add voice + vibration feedback** | Voice (TTS speaks directional cues like "Chair, 2 meters, left") + vibration (phone buzzes stronger when objects are closer) |
| 6 | **Add user preferences** | Configurable object filters, distance thresholds, feedback modes, speech settings |
| 7 | **Technical evaluation** | Measure mAP, FPS, distance MAE, model size, battery consumption |
| 8 | **User study** | Test with visually impaired participants using SUS, task completion, collision count |

#### What Success Looks Like

| Metric | Target | Example |
|--------|--------|---------|
| **mAP@0.5** | ≥ 0.70 on custom test set | "YOLOv8n achieves 0.74 mAP on navigation-relevant classes" |
| **FPS** | ≥ 10 FPS on mid-range Android | "Achieves 12 FPS on Samsung Galaxy A54" |
| **Distance MAE** | < 1.0 meter within 3m range | "Mean absolute error of 0.7m for objects within 3 meters" |
| **SUS Score** | ≥ 68 (above average usability) | "System received SUS score of 72.5" |
| **Task Completion** | ≥ 80% obstacle course navigation | "85% of participants completed the course without collision" |
| **Collision Count** | Significant reduction vs. unassisted | "Collisions reduced by 60% compared to unassisted baseline" |

---

### System Architecture

Full diagram and technical flow details... [Content truncated for brevity, same as original]

---

### References (APA 7 Format)

Abidi, M. H., Siddiquee, A. N., Alkhalefah, H., & Srivastava, V. (2024). A comprehensive review of navigation systems for visually impaired individuals. *Heliyon*, *10*(11), e31825. https://doi.org/10.1016/j.heliyon.2024.e31825

Avila, M., Wolf, K., Brock, A., & Henze, N. (2016). Remote assistance for blind users in daily life: A survey about Be My Eyes. In *Proceedings of the 9th ACM International Conference on PErvasive Technologies Related to Assistive Environments (PETRA '16)* (pp. 1–8). ACM. https://doi.org/10.1145/2910674.2935839

Baig, M. S. A., Gillani, S. A., Shah, S. M., Aljawarneh, M., Khan, A. A., & Siddiqui, M. H. (2024). AI-based wearable vision assistance system for the visually impaired: Integrating real-time object recognition and contextual understanding using large vision-language models. *arXiv preprint arXiv:2412.20059*. https://arxiv.org/abs/2412.20059

Das, D., Das, A. D., Sadaf, F., Uddin, A., & Mondal, T. (2025). Real-time assistive navigation for the visually impaired: A scalable approach for indoor and outdoor mobility. *arXiv preprint arXiv:2504.20976*. https://arxiv.org/abs/2504.20976

Gao, Y., Wu, D., Song, J., Zhang, X., Hou, B., Liu, H., Liao, J., & Zhou, L. (2025). A wearable obstacle avoidance device for visually impaired individuals with cross-modal learning. *Nature Communications*, *16*, 2857. https://doi.org/10.1038/s41467-025-58085-x

Li, J., Zheng, M., Dong, D., & Xie, X. (2025). PC-CS-YOLO: High-precision obstacle detection for visually impaired safety. *Sensors*, *25*(2), 534. https://doi.org/10.3390/s25020534

Narayanan, A., Qiao, F., Aldas, N. D. T., Shi, Y., Mahdavi, M., Itti, L., & Narayanan, V. (2024). NaviSense: A multimodal assistive mobile application for object retrieval by persons with visual impairment. In *Proceedings of the 27th International ACM SIGACCESS Conference on Computers and Accessibility* (pp. 1–21). ACM. https://doi.org/10.1145/3663547.3759726

Li, Z., Han, F., & Zheng, K. (2025). An RGB-D camera-based wearable device for visually impaired people: Enhanced navigation with reduced social stigma. *Electronics*, *14*(11), 2168. https://doi.org/10.3390/electronics14112168

Shafique, S., Bailo, G. L., Zanchi, S., Barbieri, M., et al. (2025). SnapStick: Merging AI and accessibility to enhance navigation for blind users. *MDPI Technologies*, *13*(7), 297. https://doi.org/10.3390/technologies13070297

Spiers, A. J., Quinn, R., Murtough, S., de Winton, H., Ellis-Frew, B., & Zane, S. (2024). A shape-changing haptic navigation interface for vision impairment. *Scientific Reports*, *14*, 29223. https://doi.org/10.1038/s41598-024-79845-7

Wang, W., Jing, B., Yu, X., Sun, Y., Yang, L., & Wang, C. (2024). YOLO-OD: Obstacle detection for visually impaired navigation assistance. *Sensors*, *24*(23), 7621. https://doi.org/10.3390/s24237621

Zhang, H., Falletta, N. J., Xie, J., Yu, R., Lee, S., Billah, S. M., & Carroll, J. M. (2024). Enhancing the travel experience for people with visual impairments through multimodal interaction: NaviGPT, a real-time AI-driven mobile navigation system. *arXiv preprint arXiv:2410.04005*. https://arxiv.org/abs/2410.04005
