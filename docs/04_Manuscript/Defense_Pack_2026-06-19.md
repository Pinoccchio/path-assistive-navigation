# Defense Pack: Title Proposal Defense

## Source of Truth

- Actual defense deck: `docs/04_Manuscript/MAO NANI SYA.pdf`
- Main manuscript content: `docs/04_Manuscript/Assistive_Navigation_Thesis_Ch1_Ch3.md`
- This guide is for oral defense prep, not for final manuscript wording.

## Core Story of the Study

Your study proposes an **offline, smartphone-based assistive navigation system** for visually impaired users. The core problem is that many existing solutions either:

- detect objects but do not estimate distance well,
- depend on cloud processing and become unsafe when delayed,
- overload the user with too many alerts,
- or require expensive hardware.

Your proposed answer is:

- on-device object detection,
- approximate distance-zone estimation,
- priority-based filtering,
- multimodal feedback using speech and vibration,
- and optional location context that is not required for safety-critical alerts.

The simplest one-line defense summary is:

> We are proposing a mobile assistive navigation prototype that keeps obstacle detection and warning on the device, so feedback remains fast, private, and usable even without internet.

## What You Must Keep Straight

- This is a **proposal defense**, not a final implementation defense.
- You should say **“the system proposes,” “the prototype will,” “the study aims to,”** unless you are clearly referring to literature findings.
- Do not accidentally present planned metrics as already achieved results.
- The novelty is not “we invented object detection.” The novelty is the **combination and design focus**:
  - offline-first mobile deployment,
  - distance-zone guidance,
  - priority engine,
  - multimodal feedback,
  - optional context layer.

## Slide-by-Slide Explainer

### Slide 1: Title

**What it means**

This introduces the project as an Edge-AI or on-device assistive navigation system for visually impaired users.

**Why it is there**

The panel needs to immediately understand your topic, target users, and technical direction.

**What you should say**

“This study focuses on developing an on-device mobile assistive navigation system for visually impaired users. The emphasis is on edge AI, meaning the core detection and warning functions happen directly on the smartphone instead of relying on cloud processing.”

**What the panel should understand**

- It is a mobile AI accessibility study.
- It is centered on safety, usability, and offline operation.

### Slide 2: Introduction

**What it means**

This slide establishes the practical problem and scale of need. It says visually impaired users still face mobility risks because existing tools have limited obstacle range or delayed feedback.

**Why it is there**

You need to prove the topic is socially important and technically relevant.

**What you should say**

“Vision is a major source of spatial awareness, so when vision is impaired, mobility becomes much harder. Traditional aids like white canes remain valuable, but they can miss mid-air or farther hazards. At the same time, many AI-based tools are either cloud-dependent or hardware-heavy. That is why a low-cost smartphone-based offline assistive system is worth studying.”

**Defense tip**

If asked about the numbers, say:

“According to the WHO fact sheet updated on February 10, 2026, at least 2.2 billion people globally have near or distance vision impairment, and at least 1 billion cases could have been prevented or are still unaddressed.”

### Slide 3: Statement of the Problem

**What it means**

This defines the four main literature-backed barriers:

- poor distance awareness,
- cloud fragility,
- information overload,
- hardware cost.

It also translates those barriers into six research questions.

**Why it is there**

The panel must see that your research questions come from real gaps, not random feature ideas.

**What you should say**

“From the literature, we identified four core barriers: many systems detect objects but not usable distance zones, many depend on cloud connectivity, many overwhelm users with too many alerts, and many need expensive hardware. Our research questions are directly built around solving those barriers in a practical smartphone prototype.”

**Key defense logic**

Problem -> questions -> objectives -> methodology  
That chain must stay consistent.

### Slide 4: Objectives

**What it means**

This slide converts the research questions into implementation goals.

**Why it is there**

It shows you have a structured research direction, not just a vague app idea.

**What you should say**

“Our objectives are to design the offline architecture, build on-device detection, classify obstacles into distance zones, prioritize hazards, provide multimodal feedback, add optional location context, and define evaluation procedures for technical performance and usefulness.”

**Likely panel check**

They may ask why location awareness is included.  
Answer: “It is optional contextual support, not part of immediate hazard avoidance.”

### Slide 5: Scope and Delimitations

**What it means**

This slide protects the study from overclaiming.

**Why it is there**

A strong proposal clearly states what the system will and will not do.

**What you should say**

“Our scope is limited to Android smartphones using the rear camera, with YOLOv8 and MiDaS through TensorFlow Lite, plus TTS and vibration. The study does not claim LiDAR-level precision, does not initially support iOS, and is meant as a supplementary aid rather than a replacement for white canes or mobility training.”

**This slide matters a lot**

If challenged, come back here. This is your safety slide.

### Slide 6: Review of Related Literature Overview

**What it means**

This summarizes the research landscape. It says assistive navigation is shifting from passive tools to smart, sensor- and AI-assisted systems.

**Why it is there**

It shows that your proposal is part of an active research direction.

**What you should say**

“The literature shows a clear shift from passive mobility aids toward smart electronic travel aids using deep learning, multimodal sensing, and accessibility-centered interaction design. At the same time, the literature also shows recurring bottlenecks like latency, power usage, outdoor complexity, and user stigma.”

**What not to do**

Do not spend too long explaining TAM, SAM, or SOM unless the panel asks. The real message is the transition in assistive technology trends.

### Slide 7: YOLO-Based Obstacle Detection

**What it means**

This slide explains why YOLO-based detection is relevant. It highlights literature showing improvements in small-object and thin-hazard detection.

**Why it is there**

You need to justify your object detection direction technically.

**What you should say**

“YOLO remains relevant because it balances speed and detection quality, which is important for mobile assistive navigation. The reviewed studies also show that recent variants improved handling of small or thin hazards, which matters because missing poles, wires, or narrow obstacles can create safety risks.”

**Safe technical phrasing**

Say “YOLO-based models are suitable for mobile obstacle detection because they are designed for efficient real-time vision tasks.”

Avoid saying your system already achieves a specific latency unless you have measured it.

### Slide 8: Spatial Segmentation and Pathfinding

**What it means**

This slide justifies depth estimation and offline routing ideas.

**Why it is there**

Detection alone is not enough. The user also needs spatial meaning: where is the obstacle and how urgent is it?

**What you should say**

“This slide supports the spatial side of the system. It shows that researchers are moving beyond raw object labels toward safer path interpretation using segmentation, pathfinding, and depth-aware reasoning. For our study, this supports the idea that distance-zone estimation is necessary, not optional.”

### Slide 9: Wearable Systems and Hardware

**What it means**

This slide shows that some strong systems use extra hardware, but that creates cost, stigma, and convenience issues.

**Why it is there**

It justifies why your study prefers a smartphone-first architecture.

**What you should say**

“Some high-performing systems use wearables and custom hardware, but those can increase cost, bulk, and social stigma. Our proposal intentionally explores how much assistive value can be achieved using hardware many users already own: a smartphone.”

**Panel angle**

If they ask “Why not use a smart cane or RGB-D camera?” answer:

“Those may improve precision, but they also reduce accessibility and scalability. Our study prioritizes practical deployability.”

### Slide 10: Non-Visual HMI and Spatial Mapping

**What it means**

This slide supports multimodal or non-visual interaction, especially haptics.

**Why it is there**

Your users cannot rely on screen-based output. So your interface design must also be defended.

**What you should say**

“Navigation assistance for visually impaired users depends not only on detection accuracy but also on how the information is delivered. The literature supports non-visual interaction, especially haptic guidance, because audio alone can create overload or fail in noisy environments.”

**Important phrase**

“The app is not just a vision model. It is a perception-to-feedback system.”

### Slide 11: Edge vs Cloud Trade-offs

**What it means**

This is one of your strongest justification slides. It compares edge processing and cloud VLM pipelines.

**Why it is there**

It explains your architectural choice in a direct, decision-oriented way.

**What you should say**

“Cloud systems may provide richer open-ended descriptions, but navigation safety needs dependable low-latency feedback. That is why our core safety functions are designed for edge processing. For this use case, reliability and response time are more important than open-ended semantic detail.”

**Best defense line**

“For obstacle avoidance, delayed intelligence is unsafe intelligence.”

**Important caution**

Do not present the exact `< 50ms` or `0.5s-2.0s` values as your own measured system results. Present them as trade-off framing from the reviewed architecture patterns.

### Slide 12: Research Design

**What it means**

This slide tells the panel how the study will be conducted.

**Why it is there**

Without methodology, the topic becomes just a concept pitch.

**What you should say**

“The study uses a developmental-evaluative design because we are both building a prototype and assessing its technical and usability performance. We selected a spiral model because iterative refinement fits AI-assisted mobile prototyping. For usability, purposive sampling is appropriate because the intended users are specific.”

**Likely question**

Why not experimental only?  
Answer: “Because this phase includes both prototype development and evaluation, not only hypothesis testing.”

### Slide 13: Conceptual Framework

**What it means**

This is the system pipeline.

**Why it is there**

It shows you understand how data flows through the proposed system.

**What you should say**

“Live frames and optional GPS data enter the system. Frames are preprocessed, then object detection and depth estimation run on-device. After that, the system maps direction and proximity zones, ranks obstacles through a priority layer, and finally delivers multimodal feedback while also logging evaluation metrics.”

**Panel target**

They may ask where the main contribution is.  
Answer: “In the integration logic, especially the transition from raw detections into ranked actionable alerts.”

### Slide 14: Methodology - Scoring Engine and Feedback

**What it means**

This slide explains how your priority logic works and how each zone triggers feedback.

**Why it is there**

The panel needs to see that “priority engine” is not a buzzword but an operational decision layer.

**What you should say**

“Not every detected object should be announced equally. Our scoring engine weighs proximity, direction, and hazard type. The highest-priority obstacle becomes the active alert. The feedback encoding is then matched to urgency: strong vibration and urgent speech for danger, moderate cues for caution, and suppressed or softer cues for safe conditions.”

**Simple formula explanation**

“Wdist means closeness, Wdir means whether it is in the walking path, and Whaz means how dangerous that object type is.”

**Non-math explanation**

You do not need to explain this as difficult math. Present it as a ranking rule.

`Pscore = Wdist + Wdir + Whaz`

means the system gives each detected obstacle a total priority score.

It asks three simple questions:

1. How close is the obstacle?
2. Is it directly in the user's path?
3. How dangerous is that type of obstacle?

Then it adds those three values.

The obstacle with the highest total score is the one the system warns about first.

**Meaning of each part**

- `Wdist`
  - distance weight
  - higher if the obstacle is very near
- `Wdir`
  - direction weight
  - higher if the obstacle is in the center or directly ahead
- `Whaz`
  - hazard weight
  - higher if the obstacle is more dangerous, like stairs or vehicles

**Very simple example**

Example 1: stairs ahead and very near

- `Wdist = 5`
- `Wdir = 4`
- `Whaz = 5`
- `Pscore = 14`

Example 2: chair at the side and farther away

- `Wdist = 2`
- `Wdir = 1`
- `Whaz = 2`
- `Pscore = 5`

Since `14` is higher than `5`, the system warns about the stairs first.

**Why this formula is important**

Without this scoring logic, the app may announce too many objects at once. The formula helps the system choose the most urgent obstacle first, which reduces overload and makes the warning more useful.

**Best defense answer**

"This is not advanced math. It is just a scoring rule that ranks obstacles based on closeness, direction, and danger. The one with the highest score becomes the priority warning."

### Slide 15: Evaluation

**What it means**

This slide explains how you will know whether the prototype is technically acceptable and usable.

**Why it is there**

Without measurable evaluation, the proposal lacks rigor.

**What you should say**

“We will evaluate the system using technical metrics like inference latency, FPS, and detection accuracy, usability measures like SUS and task-based errors, and context-layer checks like GPS update success and reverse-geocoding usefulness. This allows us to assess not only whether the AI runs, but whether it is actually helpful.”

**Critical distinction**

Say “will be measured,” not “was measured,” unless you already have results.

### Slide 16: Closing

**What it means**

This is the handoff to questioning.

**Why it is there**

It ends the narrative and signals confidence.

**What you should say**

“In summary, our proposal responds to major gaps in current assistive navigation systems by focusing on offline operation, practical smartphone deployment, spatial awareness, and user-centered feedback. We are now ready to clarify the study design and feasibility.”

## Manuscript Meaning by Chapter

### Chapter 1: Introduction

**Main purpose**

To prove the study is relevant, needed, and researchable.

**What each section is doing**

- **Background of the Study**
  - explains the real-world mobility problem,
  - introduces object detection, depth estimation, offline use, and multimodal feedback,
  - builds the need for the proposed prototype.
- **Statement of the Problem**
  - translates the broad issue into research questions.
- **Objectives**
  - converts those questions into actionable goals.
- **Significance**
  - explains who benefits and how.
- **Scope and Limitations**
  - prevents overclaiming and defines realistic boundaries.

**Defense meaning**

Chapter 1 answers:

- Why this topic?
- What exactly is the problem?
- What is the study trying to build or prove?

### Chapter 2: Review of Related Literature

**Main purpose**

To prove the proposal is grounded in current research and that the chosen design choices are justified.

**Main literature themes**

- assistive navigation systems,
- obstacle detection,
- offline mobile AI,
- GPS and location context,
- distance estimation,
- multimodal feedback,
- priority-based alerts,
- personalization.

**Defense meaning**

Chapter 2 answers:

- Why YOLO?
- Why offline?
- Why depth or distance zones?
- Why haptics?
- What gap still remains?

**Most important RRL conclusion**

The gap is not just obstacle detection. The real gap is **practical and usable mobile assistive navigation** that is:

- offline,
- spatially aware,
- low-overload,
- and deployable on common devices.

### Chapter 3: Methodology

**Main purpose**

To prove the proposal can be built and evaluated in a rigorous way.

**Main components**

- developmental-evaluative design,
- spiral model,
- system architecture,
- tools and technologies,
- location-aware feature design,
- dataset and training plan,
- priority engine,
- evaluation metrics,
- respondents and procedures.

**Defense meaning**

Chapter 3 answers:

- How will you build it?
- How will you test it?
- How will you know if it works?

## Best Short Answers for Likely Panel Questions

### Why this topic?

“Because visually impaired users still face immediate obstacle-awareness problems that traditional tools and many current digital systems do not fully solve. We want to explore a practical offline smartphone-based solution that is lower-cost and more deployable.”

### Why offline?

“Because obstacle avoidance is a time-sensitive safety task. Internet delay, packet loss, and cloud dependency can make feedback late or unavailable. Offline processing improves reliability, privacy, and responsiveness.”

### Why not just use cloud AI or VLMs?

“Cloud VLMs are strong for rich descriptions, but our use case is immediate hazard warning, where dependable low latency matters more than open-ended reasoning.”

### Why YOLOv8?

“Because YOLO-style detectors are widely used for efficient real-time object detection and are suitable for mobile deployment. The proposal uses YOLO as a practical edge-vision backbone, not as a claim of novelty by itself.”

### Why MiDaS or distance zones instead of exact distance?

“A smartphone monocular camera does not provide LiDAR-level precision. That is why the study focuses on approximate distance zones, which are more realistic and still actionable for warning design.”

### Why multimodal feedback?

“Because audio alone can overload users or fail in noisy settings. Combining speech and vibration improves clarity and gives the user another non-visual channel.”

### What is the novelty of the study?

“The novelty is in the integrated design for an offline-first mobile assistive prototype: on-device detection, distance-zone reasoning, a priority engine, multimodal feedback, and optional context support in one practical architecture.”

### Why Android only?

“Android is more practical for initial prototyping, device access, and TensorFlow Lite deployment. Limiting the first version to Android keeps the study feasible.”

### Why include GPS if the system is about obstacle detection?

“GPS is not used for immediate obstacle avoidance. It is included only as optional contextual support and session history.”

### How will you evaluate the prototype?

“We will use technical metrics such as latency, FPS, and detection accuracy, plus usability measures such as SUS and task-based performance, and location-context checks where relevant.”

### Is this replacing the white cane?

“No. The study clearly positions the app as a supplementary aid, not a replacement for white canes, guide dogs, or formal mobility training.”

## Weak Points and How to Defend Them

### 1. The deck sometimes sounds more finished than the manuscript

**Risk**

Some slide wording can sound like the system is already fully realized.

**Fix**

In speaking, consistently say:

- “the proposed system”
- “the prototype will”
- “the study aims to evaluate”

### 2. Exact performance claims may be challenged

**Risk**

Phrases like “sub-25ms” or hard latency values can be challenged if you have not yet measured them on your own device.

**Fix**

Say:

“Low latency is a design goal supported by edge-AI literature. Exact measured values will be established during implementation and testing.”

### 3. Distance estimation on a phone can be questioned

**Risk**

The panel may say monocular depth is not precise enough.

**Fix**

Say:

“That is exactly why the study uses distance zones rather than claiming exact meter-perfect measurement. The design is matched to realistic mobile constraints.”

### 4. Novelty can be questioned

**Risk**

If you claim “object detection for the blind” as novel, the panel can easily reject that claim.

**Fix**

Say:

“Object detection itself is not novel. Our contribution is the offline-first integrated architecture and priority-based feedback design for a practical smartphone prototype.”

### 5. Sample and testing feasibility can be questioned

**Risk**

The panel may ask whether visually impaired participants are available.

**Fix**

Say:

“Direct recruitment is intended if ethically approved and feasible. If not, the methodology already acknowledges controlled preliminary testing as a limitation, not as a substitute for actual visually impaired user evaluation.”

## Claims You Should Phrase Carefully

### Safe to say strongly

- WHO reports at least 2.2 billion people globally have near or distance vision impairment, with at least 1 billion cases preventable or unaddressed.
- Traditional mobility aids remain valuable but have limited detection range for some hazards.
- Cloud dependency can be problematic for safety-critical, real-time navigation use cases.
- Smartphone-only systems are more accessible than systems requiring specialized hardware.
- Multimodal feedback is well motivated for visually impaired assistive systems.

### Better to soften

- “Our system guarantees sub-25ms detection.”
- “Our system is safer than existing tools.”
- “YOLOv8 is the gold standard.”
- “This fully solves assistive navigation.”
- “The app accurately measures exact obstacle distance.”

### Better spoken alternatives

- “targets low-latency operation”
- “aims to improve practical obstacle awareness”
- “uses a strong and practical mobile detection approach”
- “addresses selected gaps in current systems”
- “classifies approximate distance zones”

## Fast 60-Second Defense Summary

“Our proposal focuses on developing an offline, smartphone-based assistive navigation prototype for visually impaired users. The literature shows that many existing systems either depend on cloud processing, require expensive hardware, or overwhelm the user with too many alerts. In response, we propose a system that performs object detection and approximate distance-zone estimation directly on the device, then ranks hazards using a priority engine and communicates the most urgent obstacle through speech and vibration. Optional GPS and reverse geocoding provide context, but not for safety-critical decisions. The study will be evaluated through technical metrics and usability measures to determine whether this architecture is practical, responsive, and user-centered.”

## Fast 15-Second Answer if You Freeze

“Our study proposes an offline mobile assistive navigation system that detects obstacles, estimates approximate distance zones, prioritizes the most urgent hazard, and delivers voice plus vibration feedback for visually impaired users.”

## Verified References for Defense-Sensitive Claims

- WHO fact sheet: https://www.who.int/news-room/fact-sheets/detail/blindness-and-visual-impairment
  - updated February 10, 2026
  - confirms at least 2.2 billion people have near or distance vision impairment, and at least 1 billion cases could have been prevented or are yet to be addressed
- YOLO-OD article page: https://doi.org/10.3390/s24237621
  - use this carefully as support for YOLO-based obstacle detection research
  - do not overstate its exact performance beyond what you can defend from the paper

## Final Speaking Advice

- Keep returning to the same 4-gap logic:
  - distance awareness,
  - offline reliability,
  - alert overload,
  - cost/accessibility.
- Keep repeating the same 5-part solution:
  - on-device detection,
  - distance zones,
  - priority engine,
  - multimodal feedback,
  - optional context.
- If cornered, fall back to scope and limitations.
- If challenged on precision, say the design intentionally uses **approximate warning zones**.
- If challenged on novelty, say the contribution is the **integrated offline-first assistive architecture**, not object detection alone.

## One-Page Oral Reviewer

### Spiral Model

- **Meaning**: an iterative software development model based on repeated cycles of planning, building, testing, and improving.
- **Why used in our study**: our prototype combines AI, mobile processing, and user feedback, so it needs repeated refinement rather than one-time development.
- **One-sentence defense answer**: “We used the spiral model because the system needs iterative improvement across detection, scoring, and feedback before it becomes usable.”

### Developmental-Evaluative Research Design

- **Meaning**: a research design where the study both develops a system and evaluates its performance.
- **Why used in our study**: we are not only proposing ideas; we are building a prototype and assessing how well it works.
- **One-sentence defense answer**: “It is developmental because we are building the prototype, and evaluative because we are measuring its technical and usability performance.”

### Methodology

- **Meaning**: the structured plan for how the study will be conducted.
- **Why used in our study**: it explains how we will design, build, test, and analyze the prototype.
- **One-sentence defense answer**: “Methodology is the overall plan that shows how we will carry out the study from development up to evaluation.”

### Conceptual Framework

- **Meaning**: the system map showing how inputs become processes, outputs, and evaluation.
- **Why used in our study**: it makes the system workflow clear and shows that this is more than just an app idea.
- **One-sentence defense answer**: “The conceptual framework shows how camera input is transformed into ranked obstacle alerts through the proposed processing pipeline.”

### Edge AI / On-Device AI

- **Meaning**: AI processing that happens directly on the device instead of in the cloud.
- **Why used in our study**: obstacle warnings need speed, privacy, and reliability even without internet.
- **One-sentence defense answer**: “We use edge AI so the phone can process obstacle warnings locally without depending on cloud connectivity.”

### YOLOv8

- **Meaning**: a real-time object detection model used to identify and locate objects in an image.
- **Why used in our study**: it is practical for fast mobile detection of navigation-relevant obstacles.
- **One-sentence defense answer**: “We use YOLOv8 because it is a practical real-time object detection model for mobile assistive vision tasks.”

### MiDaS

- **Meaning**: a monocular depth estimation model that predicts relative depth from a single image.
- **Why used in our study**: it helps estimate obstacle closeness without specialized depth hardware.
- **One-sentence defense answer**: “We use MiDaS to estimate relative obstacle depth from a single camera, which supports our distance-zone logic.”

### Monocular Depth Estimation

- **Meaning**: estimating depth using only one camera image.
- **Why used in our study**: it allows a smartphone-only setup instead of requiring RGB-D or LiDAR hardware.
- **One-sentence defense answer**: “Monocular depth estimation lets us estimate obstacle distance in a smartphone-based setup without extra sensors.”

### Distance-Zone Classification

- **Meaning**: classifying obstacles into approximate warning ranges such as danger, caution, or safe.
- **Why used in our study**: exact distance is harder to guarantee on a phone, but zones are realistic and usable.
- **One-sentence defense answer**: “We use distance zones because approximate warning ranges are more practical than exact meter claims in smartphone depth estimation.”

### Spatial Awareness

- **Meaning**: understanding where an object is, how far it is, and whether it is in the user's path.
- **Why used in our study**: detection alone is not enough for navigation; the system must also understand urgency in space.
- **One-sentence defense answer**: “Spatial awareness means the system does not only detect an obstacle but also interprets its location and urgency.”

### Priority Engine

- **Meaning**: the decision-making layer that ranks detected obstacles and selects the most urgent one.
- **Why used in our study**: without prioritization, the user may receive too many alerts and become overloaded.
- **One-sentence defense answer**: “The priority engine is important because it converts raw detections into a single most urgent alert that is more usable for navigation.”

### Wdist, Wdir, Whaz

- **Meaning**:
  - `Wdist` = weight for closeness
  - `Wdir` = weight for direction or path alignment
  - `Whaz` = weight for hazard level
- **Why used in our study**: these weights are the basis of the scoring logic used to rank obstacles.
- **One-sentence defense answer**: “These weights let the system score obstacles by urgency, location, and danger level instead of treating all detections equally.”

### Multimodal Feedback

- **Meaning**: using more than one communication channel, such as speech and vibration.
- **Why used in our study**: multimodal alerts are clearer and less dependent on a single sensory channel.
- **One-sentence defense answer**: “We use multimodal feedback so the system can communicate through both audio and vibration, which is more usable than audio alone.”

### Haptic Feedback

- **Meaning**: communication through touch or vibration.
- **Why used in our study**: vibration can still warn the user in noisy environments and reduces dependence on spoken output alone.
- **One-sentence defense answer**: “Haptic feedback is the vibration-based warning channel used to communicate urgency non-visually.”

### Text-to-Speech

- **Meaning**: technology that converts text into spoken audio.
- **Why used in our study**: it allows the system to announce obstacle type, direction, and warning level.
- **One-sentence defense answer**: “Text-to-Speech is the spoken-output component that reads obstacle warnings aloud to the user.”

### TensorFlow Lite

- **Meaning**: a framework for running machine learning models on mobile and edge devices.
- **Why used in our study**: it supports deployment of the AI models directly on the smartphone.
- **One-sentence defense answer**: “TensorFlow Lite is used so our AI models can run efficiently on the phone itself.”

### Purposive Sampling

- **Meaning**: choosing participants because they are directly relevant to the study.
- **Why used in our study**: the target users and evaluators must be appropriate for assistive navigation testing.
- **One-sentence defense answer**: “We use purposive sampling because the study requires participants who are relevant to the assistive navigation context.”

### Reverse Geocoding

- **Meaning**: converting latitude and longitude into readable place information.
- **Why used in our study**: it provides optional context but is not part of core obstacle avoidance.
- **One-sentence defense answer**: “Reverse geocoding is included only as optional location context, not as the main safety mechanism.”

### Latency

- **Meaning**: the delay between system input and system response.
- **Why used in our study**: obstacle warnings must arrive quickly enough to be useful.
- **One-sentence defense answer**: “Latency matters because delayed obstacle warnings can reduce the safety value of the system.”

### FPS

- **Meaning**: frames per second, or how many image frames the system processes every second.
- **Why used in our study**: it helps measure whether the app can support responsive live detection.
- **One-sentence defense answer**: “FPS shows whether the system can process live camera input smoothly enough for real-time assistive use.”

### mAP

- **Meaning**: mean Average Precision, a standard metric for object detection accuracy.
- **Why used in our study**: it helps evaluate how well the model correctly detects target obstacles.
- **One-sentence defense answer**: “mAP is used to measure how accurately the detection model recognizes navigation-relevant objects.”

### SUS

- **Meaning**: System Usability Scale, a standard usability questionnaire.
- **Why used in our study**: it gives a recognized way to measure user-perceived usability.
- **One-sentence defense answer**: “We use SUS to evaluate whether users find the prototype understandable and usable.”

### Master Answer If They Ask What Your Thesis Really Does

“This study is not only about making an app. It is about designing and evaluating an offline assistive decision pipeline where camera input is processed into obstacle detection, distance-zone interpretation, priority scoring, and multimodal feedback for visually impaired navigation.”
