# Development of a Mobile Assistive Navigation Prototype for Visually Impaired Users

Submitted in Partial Fulfillment of the Requirements for Computer Science Thesis 1

Developed by:

JAN MIKO A. GUEVARRA

LIMSAN

Bachelor of Science in Computer Science-3

MAY 2026

\pagebreak

# CHAPTER 1

# INTRODUCTION

## Background of the Study

Vision is a primary channel through which people perceive spatial information, detect hazards, and move safely through indoor and outdoor environments. When vision is impaired, everyday mobility becomes more dependent on assistive strategies, environmental familiarity, and non-visual cues. The World Health Organization reported that at least 2.2 billion people globally have a near or distance vision impairment, and at least 1 billion of these cases could have been prevented or are yet to be addressed (World Health Organization, 2026). This scale makes visual impairment not only a medical and social concern but also a technology design problem, particularly for communities where specialized assistive devices remain expensive or difficult to access.

People with visual impairment commonly rely on white canes, guide dogs, human assistance, tactile paving, and audio cues to support independent mobility. These methods remain valuable, but they also have practical limitations. White canes are effective for detecting ground-level obstacles within physical reach, yet they may not identify some head-level hazards, distant objects, or complex layouts before the user reaches them. GPS-based navigation applications can support route planning but may not detect immediate physical hazards such as chairs, stairs, poles, bicycles, vehicles, or pedestrians in the user's path. These limitations show the need for complementary assistive technologies that can provide nearby obstacle awareness in a timely and understandable manner.

Recent progress in computer vision has created new opportunities for smartphone-based assistive navigation. Object detection models such as the YOLO family are designed for efficient visual recognition and have been applied to obstacle detection systems for visually impaired users. Wang et al. (2024) proposed YOLO-OD for obstacle detection in visually impaired navigation assistance, while Li, Zheng, Dong, and Xie (2025) introduced PC-CS-YOLO for obstacle detection in visually impaired safety contexts. These studies support the relevance of object detection for navigation-related awareness, but object labels alone are insufficient. A user also needs directional and proximity information so that the system can identify which warning is most relevant.

Distance estimation is therefore a critical component of assistive navigation. Dedicated depth sensors such as RGB-D cameras and LiDAR can provide accurate distance information, but they may require additional hardware that increases cost, weight, or device complexity. Li, Han, and Zheng (2025) used RGB-D technology in a wearable navigation device, showing the value of depth-aware perception but also highlighting the specialized nature of hardware-based solutions. A smartphone-only approach can be more accessible because it uses hardware that many users already own. Monocular depth estimation models, including MiDaS, estimate relative depth from a single RGB camera image and can support distance-zone feedback when precise centimeter-level measurement is not required (Ranftl et al., 2020).

Offline operation is another important requirement. Cloud-based or internet-dependent systems may provide strong visual reasoning, but they introduce latency, connectivity dependence, privacy concerns, and possible cost barriers. NaviGPT, for example, explores vision-language models for navigation support but depends on cloud-based processing and external services (Zhang et al., 2024). NaviSense integrates multimodal object retrieval and spatial feedback, showing that richer assistive interaction is possible but also that system complexity must be considered when designing a simple mobile prototype (Sridhar et al., 2025). For an assistive navigation system intended for practical local deployment, the ability to operate directly on the device is important for reliability, privacy, and accessibility.

Feedback design is equally important. Many assistive applications rely mainly on spoken output, but audio-only feedback can overload the user, interfere with environmental hearing, or become ineffective in noisy places. Haptic feedback provides a non-visual and non-auditory channel that can alert the user through vibration patterns. Spiers et al. (2024) showed that haptic navigation interfaces can support spatial guidance for people with visual impairment. Multimodal systems that combine audio and haptic feedback may reduce dependence on a single sensory channel and help users interpret warnings faster.

This study proposes the development of an offline-first mobile assistive navigation prototype with obstacle detection, distance-zone estimation, optional location context, and multimodal feedback. The prototype will use a smartphone camera as the input sensor, a lightweight mobile-deployable object detection model, a mobile-feasible distance-zone estimation approach, TensorFlow Lite or other compatible mobile inference tooling, and Flutter for mobile application development. YOLOv8n and MiDaS-based monocular depth estimation are candidate approaches, subject to device compatibility and integration feasibility. The core obstacle-warning functions are intended to run locally on the device so that basic detection and feedback can continue even without internet access. When an internet connection is available, the system may use GPS-supported location services and online reverse geocoding to convert latitude and longitude into approximate human-readable location context such as nearby street, locality, or city names. Google Maps Platform and Mapbox document reverse geocoding as converting geographic coordinates into readable addresses or place descriptions (Google for Developers, n.d.; Mapbox, n.d.). This online location feature will be treated as optional context only and will not be required for nearby obstacle warnings. Detected objects will be classified into directional regions and distance-based warning zones, and the system will deliver feedback through text-to-speech and vibration patterns. A priority engine will rank detected obstacles based on proximity, direction, and hazard relevance so that the application can limit feedback to the most relevant warning.

## Statement of the Problem

Despite the availability of assistive navigation tools, visually impaired users still face limitations in nearby obstacle awareness, distance perception, feedback clarity, location context, and practical accessibility. Existing systems often provide partial solutions: some identify objects but do not estimate distance, some require cloud connectivity for major functions, some depend on specialized hardware, some provide GPS route information without nearby obstacle awareness, and some provide feedback without prioritizing the most relevant obstacle. These limitations can reduce the usefulness of assistive technology in actual mobility situations.

This study seeks to answer the following questions:

1. What is the architectural design of an offline-first mobile assistive navigation prototype with obstacle detection, distance-zone estimation, optional location context, and multimodal feedback?

2. How can lightweight object detection and mobile-compatible distance-zone estimation be integrated into a Flutter mobile application for on-device or offline-first obstacle warning, subject to device compatibility?

3. How can a priority engine classify detected obstacles according to distance zone, direction, and hazard relevance to reduce information overload?

4. How can audio and haptic feedback be designed to communicate obstacle warnings in a clear and usable manner?

5. How can GPS-supported location services and online reverse geocoding be used to provide approximate location context and session history without making nearby obstacle warnings dependent on internet access?

6. How can the prototype be evaluated in terms of detection performance, inference speed, distance-zone estimation, location-context usefulness, usability, and feedback clarity?

## Objectives of the Study

The general objective of this study is to design, develop, and prepare an evaluation plan for an offline-first mobile assistive navigation prototype with obstacle detection, distance-zone estimation, optional location context, and multimodal feedback.

Specifically, this study aims to:

1. Design the architecture of a smartphone-based assistive navigation prototype whose core obstacle detection and feedback functions can operate without cloud dependency.

2. Develop a Flutter mobile prototype that captures camera frames and performs on-device obstacle detection using a lightweight mobile-deployable object detection model, subject to device compatibility.

3. Integrate or simulate a mobile-feasible distance-zone estimation method to classify detected obstacles into approximate warning zones.

4. Implement a priority engine that ranks detected obstacles according to proximity, directional position, and hazard relevance.

5. Provide multimodal feedback through text-to-speech and vibration patterns that communicate object type, direction, and warning level.

6. Integrate optional GPS-based location awareness and online reverse geocoding to provide approximate location context during app use.

7. Prepare technical and usability evaluation procedures appropriate for a prototype assistive mobile application.

## Significance of the Study

This study is significant to visually impaired individuals, assistive technology practitioners, computer science students, developers, and future researchers.

For visually impaired individuals, the proposed application may serve as a supplementary mobility support tool that detects selected nearby obstacles and communicates warnings through non-visual feedback. Its offline-first core warning design may be useful in areas with unstable internet access, while its optional GPS and online reverse-geocoding features may provide approximate location context when internet access is available. Its smartphone-based implementation may also reduce dependence on specialized external hardware.

For families, caregivers, and mobility trainers, the study may provide an example of how mobile artificial intelligence can complement existing mobility practices. Optional session logs with timestamps, approximate GPS coordinates, resolved location names, and major warning events may help review where the application was used and what types of warnings were generated. The system is not intended to replace white canes, guide dogs, or formal orientation and mobility training; rather, it aims to provide supplementary information about selected nearby obstacles and approximate location context.

For assistive technology practitioners and developers, the study may contribute a practical architecture for combining object detection, monocular depth estimation, priority-based decision logic, optional reverse geocoding, session logging, and multimodal feedback in a mobile application. The design may serve as a reference for future accessibility-focused software projects.

For the field of computer science, the study applies computer vision, mobile computing, human-computer interaction, and edge artificial intelligence to a real-world accessibility problem. The priority engine and zone-based feedback design provide opportunities to evaluate how algorithmic ranking can reduce information overload in assistive systems.

For future researchers, this study may provide a foundation for work on personalized assistive navigation, improved mobile depth estimation, local dataset collection, wearable-phone integration, and broader evaluation with visually impaired users.

## Scope and Limitations of the Study

This study focuses on the design, development, and evaluation plan for a smartphone-based assistive navigation application for visually impaired users. The system will use the rear camera of an Android smartphone to detect selected navigation-relevant objects and estimate approximate distance zones. The target object categories may include persons, chairs, tables, doors, stairs, cars, bicycles, backpacks, bottles, potted plants, poles, and other common obstacles depending on dataset availability and model training feasibility. The system will also include optional GPS-based location awareness that records approximate latitude and longitude during app use and, when internet access is available, converts the coordinates into readable location names through reverse geocoding.

The system will be developed using Flutter as the mobile application framework. TensorFlow Lite will be used for on-device inference if the selected models can be deployed within target-device constraints. A lightweight object detection model will be considered for detecting selected obstacle categories, while a MiDaS-based model will be considered for monocular depth estimation. GPS access may be implemented through mobile location services, while reverse geocoding may use online services such as Android Geocoder, Google Maps Platform, Mapbox, or Flutter geocoding packages depending on availability and API requirements (Android Developers, n.d.; Google for Developers, n.d.; Mapbox, n.d.). Feedback will be delivered through text-to-speech and vibration patterns. User preferences will be included for alert behavior, feedback mode, object filtering, and location logging.

The evaluation plan will focus on technical performance and usability. Technical evaluation may include detection accuracy, inference latency, frames per second, model size, basic battery behavior or device resource observation, and distance-zone classification performance. Usability evaluation may use the System Usability Scale and task-based observation. The study will not claim real-world effectiveness until actual testing data have been collected and analyzed.

The study has several limitations. First, monocular depth estimation from a single RGB camera does not provide the same absolute precision as LiDAR, stereo cameras, or RGB-D sensors. For this reason, the system will use distance zones instead of relying entirely on exact meter-level distance. Second, object detection performance depends on lighting, camera motion, occlusion, object size, and the representativeness of the training data. Third, GPS and reverse geocoding cannot guarantee precise indoor or street-level accuracy at all times. Prior work on mobile navigation for blind and visually impaired travelers notes that GPS inaccuracy and mapping errors can create gaps between app-indicated locations and physical locations (Chen et al., 2023). Therefore, the location feature will be treated as contextual support and not as the basis for immediate obstacle avoidance. Fourth, the proposed system is intended as a supplementary aid and not as a replacement for established mobility tools. Fifth, the initial implementation will be limited to Android smartphones and may not immediately support iOS. Sixth, user testing may be constrained by the number of available respondents and ethical requirements for research involving persons with disabilities.

## Definition of Terms

Assistive Navigation. A technology-supported process that helps a user move through an environment by providing information about routes, landmarks, obstacles, or hazards.

Audio Feedback. Spoken or sound-based output produced by the system to communicate warnings, directions, or object information to the user.

Computer Vision. A field of artificial intelligence that enables computers to analyze and interpret visual information from images or video.

Danger Zone. A warning category used by the system to indicate that a detected obstacle is estimated to be close enough to require user attention.

Distance Estimation. The process of determining the approximate distance or depth relationship between the user and an object detected by the camera.

Flutter. A cross-platform mobile application development framework used to build the proposed Android application.

Geolocation. The process of determining the approximate geographic position of a device using signals such as GPS, Wi-Fi, cellular networks, or other location services.

Haptic Feedback. Feedback delivered through vibration or touch-based signals. In this study, haptic feedback refers to phone vibration patterns used to warn the user about nearby obstacles.

MiDaS. A family of monocular depth estimation models that infer relative depth from a single RGB image.

Monocular Depth Estimation. A computer vision method that estimates depth information using only one camera image.

Multimodal Feedback. The use of more than one feedback channel. In this study, multimodal feedback refers to the combination of audio feedback and haptic feedback.

Object Detection. A computer vision task that identifies object categories and their locations in an image or video frame.

Offline Inference. Machine learning prediction performed locally on the device without sending data to a cloud server.

Priority Engine. A decision-making component that ranks detected obstacles based on factors such as distance, direction, and hazard relevance.

Reverse Geocoding. The process of converting latitude and longitude coordinates into a human-readable address or approximate place description.

Session Log. A local record of app usage events, which may include timestamps, approximate location, detected high-priority obstacles, warning zones, and feedback triggers.

TensorFlow Lite. A set of tools for running machine learning models on mobile, embedded, and edge devices.

Lightweight YOLO Model. A compact object detection model from the YOLO family considered for mobile deployment and selected obstacle detection.

\pagebreak

# CHAPTER 2

# REVIEW OF RELATED LITERATURE

The reviewed literature was selected from recent peer-reviewed studies, preprints, and official technical documentation related to assistive navigation, object detection, depth estimation, haptic feedback, mobile deployment, and geolocation services. Sources were prioritized when they had accessible publisher pages, DOI links, arXiv records, official documentation pages, or dataset pages.

## Assistive Navigation for Visually Impaired Users

Assistive navigation research aims to improve independent mobility by providing non-visual information about the user's surroundings. Traditional tools such as white canes and guide dogs remain important, but recent studies show increasing interest in computer vision, wearable sensors, mobile applications, haptic devices, and vision-language models. These technologies attempt to detect obstacles, interpret environments, and deliver guidance through audio, tactile, or multimodal feedback.

The global need for accessible navigation systems is supported by the scale of vision impairment. The World Health Organization (2026) reported that at least 2.2 billion people have near or distance vision impairment. This condition can affect independence, education, employment, and social participation. Technology interventions aligned with accessibility and inclusion therefore support broader goals of reducing inequality and improving quality of life.

Several recent studies have explored assistive systems for visually impaired users. Spiers et al. (2024) evaluated a shape-changing haptic navigation interface and demonstrated the potential of touch-based guidance for spatial navigation. Gao et al. (2025) developed a wearable obstacle avoidance device using cross-modal learning and emphasized the importance of fast response for preventing collisions. Li, Han, and Zheng (2025) proposed an RGB-D camera-based wearable device with multimodal interaction and a design focus on reducing social stigma. These studies indicate that assistive navigation is moving beyond simple object labeling toward integrated perception, feedback, and user experience design.

However, many assistive systems still face adoption barriers. Specialized wearable devices can be costly, bulky, or socially noticeable. Some systems require additional sensors that are unavailable on standard smartphones. Others depend on continuous internet access or complex user interaction. These constraints motivate the development of smartphone-based systems that operate offline for nearby obstacle-warning functions while allowing internet-assisted services only for supplemental features such as readable address context, map display, or session history.

## Object Detection for Navigation Hazards

Object detection is a core technology in vision-based assistive navigation because it enables the system to identify obstacles in the camera view. Timely performance is important because a delayed warning may no longer match the user's current surroundings. YOLO models are frequently used in this area because they process images in a single-stage detection pipeline, making them suitable for low-latency applications.

Wang et al. (2024) proposed YOLO-OD, an obstacle detection approach for visually impaired navigation assistance. Their work focused on improving the detection of navigation hazards in complex environments. The study supports the relevance of YOLO-based architectures for obstacle awareness but also shows that detection accuracy must be considered alongside practical navigation needs. A system that detects many objects may still be difficult to use if it does not select which warning matters most.

Li, Zheng, Dong, and Xie (2025) proposed PC-CS-YOLO for high-precision obstacle detection for visually impaired safety. Their study addressed complex street environments and compared detection performance with other models. The study emphasizes that visually impaired navigation requires attention to real-world conditions, including small or difficult-to-detect hazards.

For the proposed study, a lightweight YOLO model is considered because the YOLO family supports deployment-oriented object detection workflows, including model export options for mobile formats (Ultralytics, n.d.). The purpose is not to develop a new object detection architecture but to integrate a practical detection model into an offline-first assistive navigation pipeline. This aligns the study with applied computer science objectives: selecting, adapting, and evaluating a feasible model for mobile use.

## Mobile and Offline-First Artificial Intelligence

Mobile assistive systems must consider latency, privacy, connectivity, and device limitations. Cloud-based systems can access powerful models, but they may introduce delays and require internet connectivity. In navigation scenarios, latency is critical because the user continues moving while the system processes information. An obstacle warning that arrives late may become inaccurate or unsafe.

TensorFlow Lite is designed for deploying machine learning models on mobile and edge devices. The TensorFlow Lite guide describes it as a set of tools that helps developers run models on mobile, embedded, and edge devices (TensorFlow, n.d.). On-device inference can reduce the need to transmit camera frames to remote servers, which supports privacy and reduces dependence on network quality.

Zhang et al. (2024) explored NaviGPT as an AI-driven mobile navigation system for persons with visual impairment. The system demonstrates the potential of advanced AI for scene reasoning, but the use of cloud-based models illustrates a key limitation for time-sensitive assistive navigation. In contrast, the proposed study prioritizes local inference using lightweight models. This limits the complexity of reasoning that the system can perform, but it improves feasibility for offline operation.

Offline-first AI also supports deployment in locations with unstable or unavailable internet access. In the Philippine context, this is important because connectivity quality can vary by location, building, and socioeconomic condition. A navigation tool designed for accessibility should not become unusable simply because the network is weak. For this reason, the proposed application will perform obstacle detection, depth estimation, priority ranking, and feedback generation locally on the smartphone when feasible. Internet access may still be used for non-critical services such as reverse geocoding and map visualization, but these services will not be required for immediate obstacle warnings.

## GPS, Reverse Geocoding, and Location Context

GPS and mobile location services can provide broader navigation context that camera-based obstacle detection cannot provide by itself. While computer vision can identify nearby hazards, it does not inherently know the user's street, barangay, city, or route history. A location-aware assistive application can combine local obstacle awareness with approximate place context, allowing the user or researcher to know where the app was used and what warning events occurred in that area.

Reverse geocoding is the process of converting coordinates into readable address information and may require internet access depending on the provider and device environment. Google Maps Platform describes reverse geocoding as translating a map location into a human-readable address, while Mapbox describes reverse geocoding as converting longitude and latitude into a place name or address (Google for Developers, n.d.; Mapbox, n.d.). Android also provides a Geocoder class for geocoding and reverse geocoding, although the amount of detail in returned addresses may vary (Android Developers, n.d.). Flutter applications can access device location through packages such as Geolocator and convert coordinates into placemarks through geocoding packages (Baseflow, n.d.-a; Baseflow, n.d.-b).

For the proposed study, GPS and online reverse geocoding are useful as contextual features rather than immediate safety mechanisms. The application may record that the user is near a particular street, such as Abad Santos Street, and associate this location with timestamps and detected warning events. This can support visual map review, session history, and research analysis when internet access is available. However, GPS should not be treated as precise obstacle-level guidance. Chen et al. (2023) reported that GPS inaccuracy and mapping errors can create gaps when blind and visually impaired travelers use mobile navigation to locate bus stops. This finding supports the need to separate macro-location context from micro-navigation and obstacle avoidance. In the proposed system, GPS provides approximate location context, while camera-based computer vision provides immediate obstacle awareness.

## Distance Estimation and Spatial Awareness

Object detection provides labels and bounding boxes, but it does not automatically tell the user how close an object is. For navigation, distance is essential because the same object may require different responses depending on proximity. A chair three meters away may not require urgent action, while a chair directly in front of the user may need immediate warning.

Depth-aware systems can use specialized sensors. Li, Han, and Zheng (2025) used RGB-D sensing in a wearable navigation device, showing the value of hardware depth information for obstacle avoidance. However, RGB-D hardware is not available in most smartphones and may increase system cost. A smartphone-only approach requires another method for estimating depth.

Monocular depth estimation offers a software-based alternative. Ranftl et al. (2020) introduced a robust monocular depth estimation approach that mixes datasets for zero-shot transfer, forming the basis for the MiDaS model family. MiDaS estimates relative depth from a single RGB image, making it suitable for camera-only systems. Although monocular depth does not provide perfect absolute distance, it can support zone-based warnings that group obstacles into practical categories such as danger, caution, and safe.

The proposed study will use distance zones rather than relying exclusively on exact distance values. This is a pragmatic design decision. Users need actionable warnings, and approximate zones can be more reliable and understandable than precise but unstable measurements. Zone-based alerts also support consistent haptic patterns, where stronger or more frequent vibration indicates greater urgency.

## Multimodal Feedback and Haptic Guidance

Feedback is a central issue in assistive navigation. A technically accurate detection system can still fail if its warnings are confusing, late, excessive, or difficult to perceive. Audio feedback is common because it can describe object type and direction using natural language. However, audio may interfere with environmental hearing or become ineffective in noisy places.

Haptic feedback provides an additional communication channel. Spiers et al. (2024) evaluated haptic navigation interfaces and found that touch-based spatial cues can support navigation tasks. Haptic feedback is particularly useful because it can be perceived without looking at a screen and without fully occupying the auditory channel. For visually impaired users, this is important because environmental sound may already be used for orientation and safety.

NaviSense also demonstrates the relevance of multimodal feedback. Sridhar et al. (2025) described a system that combines open-world object detection with audio-haptic guidance for object retrieval. While NaviSense is focused on object retrieval and uses technologies not available on all smartphones, it suggests that audio-haptic guidance is a practical design direction for visually impaired users.

The proposed system will use multimodal feedback in a simplified and mobile-feasible way. Audio feedback will communicate object type, direction, and warning level. Haptic feedback will encode urgency through vibration pattern. For example, a nearby obstacle in the danger zone may trigger a stronger repeated vibration, while a less urgent obstacle may trigger a shorter vibration or no vibration depending on user preference.

## Priority-Based Alerts and Information Overload

One of the major challenges in assistive navigation is information overload. A camera frame may contain several objects, but announcing all of them can distract or overwhelm the user. A useful system must decide which obstacle should be communicated first. This requires a priority mechanism.

Existing object detection studies often focus on recognition performance but do not fully address alert prioritization. A high mAP score does not automatically result in a usable warning system. For assistive navigation, priority should consider factors such as distance, object position, object type, and movement relevance. An object directly ahead and close to the user should receive higher priority than an object far away or outside the walking path.

Li, Han, and Zheng (2025) included an intelligent interaction module for identifying a core obstacle in an RGB-D wearable navigation system. This supports the idea that assistive systems should filter and prioritize information rather than presenting raw detection output. The proposed study applies this idea to a smartphone-only system by implementing a priority engine based on distance zone, direction, and hazard relevance.

The priority engine is expected to reduce alert fatigue by limiting feedback to the most relevant obstacle at a given moment. Instead of saying every detected object, the system can announce the highest-risk obstacle first and suppress low-priority alerts. This makes the feedback more actionable and reduces cognitive load.

## Personalization and User Preferences

Users with visual impairment differ in mobility skills, preferred feedback, hearing ability, walking speed, environment, and tolerance for alerts. A uniform feedback design may not fit all users. Personalization is therefore important for practical adoption.

Recent systems increasingly recognize the need for user-centered design. SnapStick, proposed by Shafique et al. (2025), combined a smartphone application, smart cane interaction, and scene description features to support navigation and environmental awareness. The study emphasizes practical concerns such as usability, feedback delivery, and user acceptance. These concerns are relevant to the proposed system because a mobile assistive application must be configurable enough to match user needs.

The proposed system will include basic user preferences such as feedback mode, speech rate, vibration settings, alert thresholds, and object filters. These preferences will not attempt to learn automatically from user behavior in the initial version, but they will allow users to adjust system behavior manually. This is a feasible starting point for personalization within the scope of a Thesis 1 project.

## Synthesis and Research Gap

The reviewed literature shows that assistive navigation research has advanced in object detection, depth sensing, haptic feedback, multimodal interaction, and AI-based scene understanding. YOLO-based systems support timely obstacle detection. RGB-D and wearable systems demonstrate the value of distance-aware perception. Haptic and audio-haptic studies show that feedback should not rely only on speech. Vision-language systems show the potential of richer scene understanding, but they may require cloud processing or more complex hardware.

Despite these advances, a gap remains for a low-cost, smartphone-based, offline-first prototype that combines object detection, approximate distance-zone estimation, priority-based warning, multimodal feedback, optional location context, session history, and user preferences in one mobile application. Many systems address only one or two of these needs. The proposed study addresses this gap by integrating a mobile object detection model, monocular depth estimation, TensorFlow Lite, Flutter, a priority engine, and an optional GPS/reverse-geocoding layer into an offline-first assistive navigation prototype.

\pagebreak

# CHAPTER 3

# METHODOLOGY

## Research Design

This study will use a developmental research design. The primary output is a mobile assistive navigation application that will be designed, implemented, and evaluated based on technical and usability criteria. The study focuses on system development rather than experimental clinical intervention. It will involve requirement analysis, system design, prototype implementation, technical testing, and usability evaluation.

The developmental design is appropriate because the study aims to produce a working software artifact. The evaluation will determine whether the system performs its intended functions: detecting selected obstacles, estimating distance zones, ranking warnings, and delivering audio-haptic feedback. The study will not claim medical effectiveness or replace professional mobility training.

## Conceptual Framework

The conceptual framework of the study is based on the relationship between mobile computer vision processing, optional location context, and non-visual user feedback. The primary input is the live camera stream from the smartphone. A secondary input is the device's approximate GPS location when the user grants permission. The processing components include object detection, depth estimation, zone classification, directional mapping, priority scoring, reverse geocoding, and session logging. The output is multimodal feedback delivered through speech and vibration, with optional map or history visualization for location context.

The independent components of the system are the camera input, object detection model, depth estimation model, priority engine, feedback configuration, GPS module, and reverse-geocoding module. The dependent evaluation outcomes are detection performance, inference speed, distance-zone correctness, location-context usefulness, usability, and perceived usefulness. The framework assumes that combining object recognition, distance awareness, prioritized feedback, and approximate location context may provide more actionable navigation support than object recognition alone.

The Technology Acceptance Model may be used as a usability lens because it focuses on perceived usefulness and perceived ease of use. In this study, perceived usefulness refers to whether users believe the application can support navigation awareness, while perceived ease of use refers to whether users can understand and operate the application with minimal difficulty.

## Software Development Process

The development of the system will follow an iterative prototyping process based on the Spiral Model. The Spiral Model is suitable because assistive technology development involves technical risk, usability risk, and repeated refinement. Each cycle will include planning, risk analysis, engineering, and evaluation.

During the planning phase, the researchers will identify target users, define system requirements, select supported object classes, determine feedback modes, and prepare the development environment. The planned technology stack includes Flutter, TensorFlow Lite or other compatible mobile inference tooling, a mobile object detection model, a mobile-feasible distance-zone estimation method, camera integration, text-to-speech, vibration support, GPS access, reverse geocoding, and local session logging.

During the risk analysis phase, the researchers will identify technical and usability risks. Technical risks include slow inference speed, increased battery use, inaccurate depth estimation, camera blur, poor lighting, model compatibility issues, weak GPS signal, reverse-geocoding failure, API rate limits, and internet unavailability. Usability risks include confusing audio messages, excessive vibration, alert fatigue, privacy concern, and overreliance on approximate GPS location. Mitigation strategies will include model optimization, zone-based distance classification, limiting feedback frequency, allowing user preferences, obtaining explicit location permission, and keeping obstacle warnings functional without internet access.

During the engineering phase, the researchers will implement the mobile application. The application will capture camera frames, run object detection, estimate depth, classify warning zones, rank obstacles, and trigger audio-haptic feedback. It will also obtain location permission, collect approximate coordinates during active sessions, convert coordinates into readable location text when internet access is available, and store selected session events locally. Development will be performed iteratively so that each component can be tested before full integration.

During the evaluation phase, the researchers will test the prototype using technical metrics and usability instruments. Technical testing will assess detection accuracy, inference latency, frames per second, distance-zone performance, location update behavior, reverse-geocoding success, and basic device resource behavior. Usability testing will assess user perception through questionnaires and observation.

## System Architecture

The proposed system architecture consists of eight main layers: input layer, inference layer, post-processing layer, priority engine, location layer, feedback layer, session log layer, and preference layer.

Figure 1 visually summarizes the interaction among the camera input, inference modules, priority engine, feedback layer, location layer, and session log layer.

```text
Camera Input + Optional GPS Permission
        |
        v
Frame Preprocessing + Location Capture
        |
        v
On-Device Inference Layer
  - Object Detection
  - Monocular Depth Estimation
        |
        v
Post-Processing Layer
  - Direction Mapping
  - Approximate Distance-Zone Classification
        |
        v
Priority Engine
  - Distance Zone
  - Direction
  - Hazard Relevance
        |
        v
Primary Feedback Candidate
        |
        +---------------------> Audio + Haptic Feedback
        |
        +---------------------> Optional Local Session Log
        |
        +---------------------> Optional Reverse-Geocoded Location Context
```

Figure 1. Proposed system architecture of the offline-first assistive navigation prototype.

The input layer captures live frames from the smartphone camera and, with permission, approximate GPS coordinates from the device's location service. Camera frames will be resized and preprocessed according to the input requirements of the detection and depth models.

The inference layer performs object detection and depth estimation. The object detection model will identify object classes and bounding boxes. The depth estimation model will estimate relative depth from the same or synchronized camera frame. Both models are intended to run locally through TensorFlow Lite if deployment compatibility and device performance allow it.

The post-processing layer maps detections to spatial information. Bounding box positions will be converted into directional labels such as left, center, and right. Depth output will be associated with detected regions and converted into distance zones such as danger, caution, and safe.

The priority engine ranks detected obstacles. Each detected object will receive a priority score based on distance zone, direction, and hazard relevance. Objects in the danger zone, objects located near the center path, and objects classified as high-risk will receive higher scores. The highest-ranked object will be selected for feedback.

The location layer collects approximate latitude and longitude during active app use. When internet access is available, reverse geocoding converts coordinates into readable context such as street, barangay, city, or landmark. If reverse geocoding fails, the system will retain coordinates and mark the address as unavailable.

The feedback layer delivers warnings to the user. Text-to-speech will produce spoken alerts such as "Chair ahead, danger zone" or "Person on the left, caution." If enabled, the application may also speak approximate location context such as "Current location near Abad Santos Street, Digos City." The vibration module will produce haptic patterns that correspond to the warning level.

The session log layer stores selected app events locally. A log entry may include timestamp, approximate latitude, longitude, resolved address, highest-priority detected object, warning zone, feedback type, and confidence values where applicable. These logs may be used for review, research analysis, and visual map history.

The preference layer stores user settings. Users may configure feedback mode, speech speed, vibration intensity if supported by the device, alert frequency, enabled object categories, location logging, and whether the application should announce current location.

## Tools and Technologies

The application will be developed using Flutter because it supports cross-platform mobile development and has packages for camera access, local storage, text-to-speech, vibration, geolocation, and geocoding. The initial target platform will be Android because Android devices are more accessible for prototype testing and TensorFlow Lite deployment.

TensorFlow Lite or other compatible mobile inference tooling will be used for on-device machine learning inference if the selected models can be converted and executed within target-device constraints. A lightweight YOLO model will be considered for object detection because of its deployment-oriented object detection workflow. A MiDaS-based or other lightweight depth-estimation approach may be considered because monocular depth estimation can infer relative depth from a single RGB image without specialized depth hardware. If mobile depth integration is not feasible, a simpler calibrated distance-zone method may be used for controlled testing. The Geolocator package may be used to obtain the device's current position, and a geocoding service may be used to convert coordinates into readable location names (Baseflow, n.d.-a; Baseflow, n.d.-b).

The dataset plan will use publicly available computer vision datasets and a small custom dataset. COCO will provide common object categories and bounding box annotations (Lin et al., 2014). Open Images may supplement categories that are not sufficiently represented in COCO. A custom campus dataset may be collected to represent local walking environments and common obstacles.

## Location-Aware Feature Design

The location-aware feature will operate as a supplemental module rather than a critical safety dependency. When the app starts a navigation session, it will request location permission from the user. If permission is granted, the system will periodically collect approximate latitude and longitude while the app is active. If permission is denied, the obstacle detection and feedback functions will continue without location logging.

When internet access is available, the system will submit coordinates to a reverse-geocoding provider to obtain readable location information. Depending on implementation constraints, the provider may be Android Geocoder, Google Maps Platform, Mapbox, or a Flutter geocoding package. The returned address may include street name, barangay or locality, city, province, and country. The app may display this information on a map/history screen and may optionally announce it through text-to-speech. If internet access is unavailable, obstacle warnings will continue without resolved address text.

To avoid overclaiming GPS accuracy, the system will label location data as approximate. The app will not use GPS to decide whether an obstacle is near the user, because immediate obstacle awareness will come from camera-based detection and depth estimation. The system will use GPS mainly for context, session review, and research logs.

The planned session log fields are: timestamp, latitude, longitude, resolved address or place name, detected object class, direction, warning zone, priority score, feedback mode, and internet/reverse-geocoding status. These logs will be stored locally and may be exported only with consent for research analysis.

## Dataset and Training Plan

The object detection model will be prepared using a combination of public and custom data. COCO will be used as the primary source for common classes such as person, chair, bicycle, car, bottle, backpack, and potted plant. Open Images V7 may be used to supplement classes not sufficiently represented in COCO, depending on annotation availability (Kuznetsova et al., 2020; Google Open Images, n.d.). The researchers may collect additional images from campus environments to improve local relevance.

The custom dataset collection will focus on common navigation scenes such as corridors, classrooms, walkways, entrances, stairs, chairs, tables, parked bicycles, and pedestrian areas. Images will be annotated using bounding boxes. The dataset will be divided into training, validation, and testing sets. The researchers will avoid collecting personally identifiable images without consent and will follow ethical guidelines for data collection.

A lightweight object detection model may be fine-tuned on selected object categories if training resources and dataset quality are sufficient. If fine-tuning is not feasible, the prototype may use a suitable pre-trained model and limit evaluation to supported object categories. After model preparation, the selected model will be exported to a mobile-compatible format when feasible. Quantization may be applied if necessary to reduce model size and improve inference speed. A MiDaS-based or other lightweight depth-estimation approach may be used if mobile integration is feasible; otherwise, the prototype will use a simpler calibrated distance-zone method for controlled testing. If exact metric distance is unstable, the system will use relative depth thresholds or controlled reference distances calibrated into practical distance zones.

## Priority Engine Design

The priority engine will convert raw detections into actionable alerts. Each detected object will be assigned a score based on three main factors: distance zone, direction, and hazard relevance.

Distance zone will receive the strongest weight because closer obstacles are more urgent. Objects in the danger zone will receive the highest score, followed by caution-zone objects, while safe-zone objects may be suppressed unless the user enables low-priority alerts.

Direction will indicate whether the object is on the left, center, or right of the camera frame. Center objects will receive higher priority because they are more likely to be in the walking path.

Hazard relevance will depend on object type. Stairs, vehicles, poles, bicycles, and chairs may receive higher default scores than objects that are less likely to block movement. These values may be adjusted in the settings.

The general scoring logic will be:

priority_score = distance_weight + direction_weight + hazard_weight

The object with the highest score will be selected as the primary feedback candidate. Repeated alerts will be controlled by a cooldown interval to avoid excessive warnings.

## Evaluation Metrics

The system will be evaluated using technical and usability metrics.

Object detection performance will be measured using precision, recall, and mAP where a labeled test dataset is available. These metrics will determine whether the model can correctly identify navigation-relevant obstacles.

Inference performance will be measured using frames per second, average inference latency, and model loading time. These metrics will determine whether the application can provide timely feedback on a target Android device.

Distance-zone performance will be measured by comparing predicted zones against observed or manually measured reference distances. Because monocular depth estimation may not provide precise absolute distance, the study will emphasize zone classification accuracy rather than exact centimeter-level precision.

Feedback performance will be evaluated by observing whether alerts are triggered correctly for selected test scenarios. The researchers will test whether danger-zone objects produce urgent feedback, caution-zone objects produce moderate feedback, and low-priority objects are suppressed when appropriate.

Usability will be evaluated using the System Usability Scale and short debriefing questions. The evaluation will focus on perceived usefulness, ease of use, clarity of feedback, comfort with vibration patterns, and perceived support for navigation awareness.

Location-context evaluation will measure whether the app successfully records approximate coordinates during active sessions, whether reverse geocoding returns understandable place names, and whether users or evaluators find the location history useful. GPS results will be assessed as contextual information, not as precise obstacle avoidance data.

## Respondents and Participants

The target participants for usability evaluation will be visually impaired users, if recruitment is approved and feasible. If direct recruitment is limited by ethical or logistical constraints, an initial technical evaluation may be performed using controlled obstacle scenarios and sighted participants under safe simulation conditions. Any simulation with sighted participants will be clearly identified as a limitation and will not be treated as equivalent to actual visually impaired user experience.

Participants must be briefed about the purpose of the study, the prototype nature of the application, and the safety limitations of the system. The application will not be used as the only navigation aid during testing. A researcher or assistant will be present to ensure safety during navigation tasks.

## Data Gathering Procedure

The data gathering procedure will begin with system preparation. The researchers will install the application on the target Android device, load the TensorFlow Lite models, configure object classes, and test the camera pipeline.

For technical testing, the researchers will prepare a set of test images, videos, or controlled obstacle scenarios. The system will process these inputs, and outputs will be recorded. Detection results, latency logs, distance-zone predictions, priority decisions, location updates, reverse-geocoding responses, and session log entries will be collected for analysis.

For usability testing, participants will be oriented on how the application works. They will perform selected tasks in a controlled environment, such as identifying or approaching obstacles while receiving system feedback. After the task, participants will answer usability questions and provide comments about the clarity and usefulness of the feedback.

All collected data will be handled confidentially. The researchers will avoid collecting unnecessary personal information. If video or image data includes identifiable individuals, consent and privacy safeguards will be applied. Location data will be collected only with permission and only during active app sessions. The manuscript and prototype documentation will clearly state that location logs are for context and evaluation, not for surveillance.

## Data Analysis Procedure

Technical data will be analyzed using descriptive statistics. Precision, recall, mAP, latency, FPS, distance-zone accuracy, location update success rate, reverse-geocoding success rate, and address usefulness ratings will be summarized using averages, percentages, and tables. Error cases will be reviewed to identify common causes such as lighting, occlusion, small object size, depth estimation instability, weak GPS signal, unavailable internet, or incomplete geocoding results.

Usability responses will be analyzed using the System Usability Scale scoring procedure. Debriefing responses will be summarized thematically to identify usability strengths, pain points, and suggested improvements. Observational notes will be used to interpret how participants responded to audio and haptic alerts.

The final analysis will compare the system outcomes against the study objectives. Since this document is limited to Thesis 1 development and methodology, results, conclusions, and recommendations will be written only after prototype implementation and evaluation have been completed.

\pagebreak

# REFERENCES

Android Developers. (n.d.). *Geocoder*. Retrieved May 24, 2026, from https://developer.android.com/reference/android/location/Geocoder

Baseflow. (n.d.-a). *Geolocator: Flutter package*. Retrieved May 24, 2026, from https://pub.dev/packages/geolocator

Baseflow. (n.d.-b). *Geocoding: Flutter package*. Retrieved May 24, 2026, from https://pub.dev/packages/geocoding

Chen, X., Jia, S., Li, H., & Yang, H. (2023). Field evaluation of a mobile app for assisting blind and visually impaired travelers to find bus stops. *arXiv preprint arXiv:2309.10940*. https://arxiv.org/abs/2309.10940

Gao, Y., Wu, D., Song, J., Zhang, X., Hou, B., Liu, H., Liao, J., & Zhou, L. (2025). A wearable obstacle avoidance device for visually impaired individuals with cross-modal learning. *Nature Communications, 16*, Article 2857. https://doi.org/10.1038/s41467-025-58085-x

Google for Developers. (n.d.). *Reverse geocoding*. Google Maps Platform Documentation. Retrieved May 24, 2026, from https://developers.google.com/maps/documentation/geocoding/reverse-geocoding

Google Open Images. (n.d.). *Open Images V7*. Retrieved May 24, 2026, from https://storage.googleapis.com/openimages/web/factsfigures_v7.html

Kuznetsova, A., Rom, H., Alldrin, N., Uijlings, J., Krasin, I., Pont-Tuset, J., Kamali, S., Popov, S., Malloci, M., Kolesnikov, A., Duerig, T., & Ferrari, V. (2020). The Open Images Dataset V4: Unified image classification, object detection, and visual relationship detection at scale. *International Journal of Computer Vision, 128*, 1956-1981. https://doi.org/10.1007/s11263-020-01316-z

Li, J., Zheng, M., Dong, D., & Xie, X. (2025). PC-CS-YOLO: High-precision obstacle detection for visually impaired safety. *Sensors, 25*(2), Article 534. https://doi.org/10.3390/s25020534

Li, Z., Han, F., & Zheng, K. (2025). An RGB-D camera-based wearable device for visually impaired people: Enhanced navigation with reduced social stigma. *Electronics, 14*(11), Article 2168. https://doi.org/10.3390/electronics14112168

Lin, T.-Y., Maire, M., Belongie, S., Bourdev, L., Girshick, R., Hays, J., Perona, P., Ramanan, D., Dollár, P., & Zitnick, C. L. (2014). Microsoft COCO: Common objects in context. *European Conference on Computer Vision*. https://arxiv.org/abs/1405.0312

Mapbox. (n.d.). *Geocoding API*. Retrieved May 24, 2026, from https://docs.mapbox.com/api/search/geocoding/

Ranftl, R., Lasinger, K., Hafner, D., Schindler, K., & Koltun, V. (2020). Towards robust monocular depth estimation: Mixing datasets for zero-shot cross-dataset transfer. *IEEE Transactions on Pattern Analysis and Machine Intelligence*. https://arxiv.org/abs/1907.01341

Shafique, S., Bailo, G. L., Zanchi, S., Barbieri, M., et al. (2025). SnapStick: Merging AI and accessibility to enhance navigation for blind users. *Technologies, 13*(7), Article 297. https://doi.org/10.3390/technologies13070297

Spiers, A. J., Quinn, R., Murtough, S., de Winton, H., Ellis-Frew, B., & Zane, S. (2024). A shape-changing haptic navigation interface for vision impairment. *Scientific Reports, 14*, Article 29223. https://doi.org/10.1038/s41598-024-79845-7

Sridhar, A. N., Qiao, F., Troncoso Aldas, N. D., Shi, Y., Mahdavi, M., Itti, L., & Narayanan, V. (2025). NaviSense: A multimodal assistive mobile application for object retrieval by persons with visual impairment. In *Proceedings of the 27th International ACM SIGACCESS Conference on Computers and Accessibility*. Association for Computing Machinery. https://doi.org/10.1145/3663547.3759726

TensorFlow. (n.d.). *TensorFlow Lite guide*. Retrieved May 24, 2026, from https://www.tensorflow.org/lite/guide

Ultralytics. (n.d.). *YOLOv8 model documentation*. Retrieved May 24, 2026, from https://docs.ultralytics.com/models/yolov8/

Wang, W., Jing, B., Yu, X., Sun, Y., Yang, L., & Wang, C. (2024). YOLO-OD: Obstacle detection for visually impaired navigation assistance. *Sensors, 24*(23), Article 7621. https://doi.org/10.3390/s24237621

World Health Organization. (2026). Blindness and vision impairment. https://www.who.int/news-room/fact-sheets/detail/blindness-and-visual-impairment

Zhang, H., Falletta, N. J., Xie, J., Yu, R., Lee, S., Billah, S. M., & Carroll, J. M. (2024). Enhancing the travel experience for people with visual impairments through multimodal interaction: NaviGPT, a real-time AI-driven mobile navigation system. *arXiv preprint arXiv:2410.04005*. https://arxiv.org/abs/2410.04005
