# PPT Guide — Five Proposed Thesis Topics

---

## SLIDE: OVERVIEW

- **Topic 1:** Skin Lesion Classification — Lightweight CNNs on Mobile Devices (SDG 3)
- **Topic 2:** Chest X-Ray Tuberculosis Detection — CNN Comparison with Grad-CAM (SDG 3)
- **Topic 3:** Deepfake Face Detection — CNN Performance on Compressed Social Media Images (SDG 16)
- **Topic 4:** Post-Disaster Building Damage Assessment — CNN vs Vision Transformer (SDG 11)
- **Topic 5:** AI-Generated Text Detection — Machine Learning vs Transformers (SDG 4)

Each topic covers:
- Introduction
- Problem Statement
- Literary Review
- Objectives
- Hypothesis
- Methodology
- Expected Outcomes
- Recommendations

---

# TOPIC 1: Skin Lesion Classification — Lightweight CNNs on Mobile Devices

---

## SLIDE: Introduction

- Skin cancer is one of the most common cancers worldwide, yet early detection remains inconsistent in areas with limited access to dermatologists.
- Most existing CNN-based studies use heavyweight models (ResNet, VGG) that are too large for mobile deployment.
- This study compares three lightweight CNN architectures — MobileNetV3, EfficientNet-Lite, and ShuffleNet — on the HAM10000 dataset.
- The best model will be deployed on a Flutter mobile app using TensorFlow Lite with Grad-CAM heatmaps for visual explainability.
- Aligned with **SDG 3: Good Health and Well-Being** — enabling accessible, low-cost skin lesion screening on mobile devices.

## SLIDE: Problem Statement

- Early detection of skin cancer significantly improves survival rates, but access to dermatologists is limited, especially in rural and underserved communities.
- Existing deep learning models for skin lesion classification (ResNet50, VGG16, DenseNet) achieve high accuracy but require 100–500 MB of storage — making them impractical for mobile devices.
- Few studies systematically compare lightweight CNN architectures specifically optimized for on-device mobile inference with integrated visual explainability.
- There is a need for a model that balances accuracy, speed, and size to enable real-time skin lesion screening directly on a smartphone without internet connectivity.

## SLIDE: Literary Review

- **Esteva et al. (2017)** demonstrated that a deep CNN can classify skin cancer at dermatologist-level accuracy, but used a heavyweight architecture (Inception v3) not suitable for mobile deployment.
- **Tschandl et al. (2018)** introduced the HAM10000 dataset with 10,015 dermoscopic images across 7 lesion classes, which has become the standard benchmark for skin lesion classification.
- **Howard et al. (2019)** proposed MobileNetV3 using hardware-aware neural architecture search (NAS), achieving competitive accuracy optimized for mobile devices (~22 MB).
- **Tan & Le (2019)** developed EfficientNet using compound scaling to balance depth, width, and resolution, later adapted as EfficientNet-Lite for mobile deployment.
- **Selvaraju et al. (2017)** introduced Grad-CAM, enabling visual explanations of CNN predictions — critical for building trust in medical AI applications.
- **Existing Gap:** No study combines a systematic comparison of lightweight architectures with on-device deployment and visual explainability for skin lesion classification.

## SLIDE: Objectives

- To compare the classification performance of three lightweight CNN architectures — MobileNetV3, EfficientNet-Lite, and ShuffleNet — on the HAM10000 skin lesion dataset.
- To evaluate each model's efficiency in terms of model size (MB) and inference time (ms) for mobile deployment.
- To integrate Grad-CAM heatmaps for visual explainability, verifying that models focus on clinically relevant lesion regions.
- To identify the optimal accuracy-to-efficiency tradeoff among the three architectures for on-device inference.
- To deploy the best-performing model on a Flutter mobile application using TensorFlow Lite for accessible, low-cost skin lesion screening.

## SLIDE: Hypothesis

- **H1:** EfficientNet-Lite will achieve the highest classification accuracy among the three lightweight models due to its compound scaling approach that balances depth, width, and resolution.
- **H2:** ShuffleNet will have the smallest model size and fastest inference time but at the cost of lower classification accuracy compared to MobileNetV3 and EfficientNet-Lite.
- **H3:** MobileNetV3 will provide the most balanced accuracy-to-efficiency tradeoff, making it the most suitable for on-device mobile deployment.
- **H4:** Grad-CAM heatmaps will confirm that all three models focus on the lesion area rather than background skin, with higher-accuracy models producing more precise attention maps.

## SLIDE: Methodology

- **Dataset:** HAM10000 dataset (10,015 dermoscopic images, 7 lesion classes) with ISIC 9-Class dataset (2,357 images) as supplementary data for generalization testing.
- **Preprocessing:** Image resizing, normalization, and data augmentation (rotation, flipping, zooming) to address class imbalance and improve model generalization.
- **Model Training:** Fine-tune three pretrained lightweight CNNs — MobileNetV3, EfficientNet-Lite, and ShuffleNet — using transfer learning from ImageNet weights on Google Colab.
- **Evaluation Metrics:** Accuracy, F1-score per class, model size (MB), and inference time (ms) on an actual mobile device.
- **Explainability:** Generate Grad-CAM heatmaps for each model to visualize which image regions influence predictions and verify focus on lesion areas.
- **Deployment:** Convert the best-performing model to TensorFlow Lite and deploy on a Flutter Android application for real-time on-device skin lesion screening.

## SLIDE: Expected Outcomes

- A comparative performance table of MobileNetV3, EfficientNet-Lite, and ShuffleNet evaluated on accuracy, F1-score, model size (MB), and inference time (ms).
- Grad-CAM heatmap visualizations demonstrating model attention on skin lesion regions across all three architectures.
- Identification of the optimal lightweight CNN architecture for on-device skin lesion classification.
- A working Flutter mobile application prototype with TensorFlow Lite integration for real-time skin lesion screening.

## SLIDE: Recommendations

- Future studies may expand the dataset to include diverse skin tones (e.g., Fitzpatrick17k) to address the limitation of HAM10000 being predominantly Caucasian skin types.
- Explore additional lightweight architectures such as NASNet-Mobile or MobileViT (Vision Transformer) for potential accuracy improvements.
- Extend the mobile application to support iOS deployment in addition to Android for wider accessibility.
- Integrate the screening tool with telemedicine platforms to connect users with dermatologists for professional follow-up consultations.
- Conduct clinical validation with dermatologists to evaluate the real-world reliability of Grad-CAM explanations and model predictions.
- Investigate multi-language support for the app interface to serve communities in the Philippines and other non-English speaking regions.

---

# TOPIC 2: Chest X-Ray Tuberculosis Detection — CNN Comparison with Grad-CAM

---

## SLIDE: Introduction

- Tuberculosis (TB) remains a leading cause of death globally, with the Philippines ranking among the highest-burden countries.
- Deep learning models have shown strong results in chest X-ray classification, but most studies focus on multi-condition detection (e.g., CheXNet with 14 pathologies) rather than focused TB screening.
- This study compares three pretrained CNN architectures — ResNet50, DenseNet121, and EfficientNet-B0 — for binary TB detection (TB vs. Normal) using the Shenzhen and Montgomery datasets (800 images).
- Grad-CAM visualization is used to verify whether model attention aligns with radiologist-identified TB regions in the lungs.
- Aligned with **SDG 3: Good Health and Well-Being** — supporting TB screening in resource-limited settings.

## SLIDE: Problem Statement

- The Philippines has one of the highest TB incidence rates in the world, yet access to radiologists for chest X-ray interpretation remains limited in rural areas.
- Most existing deep learning studies for chest X-rays target multiple pathologies, lacking a focused and reproducible approach specifically for binary TB detection.
- Current models operate as black boxes — they predict TB but do not explain which lung regions influenced their decision, reducing trust among medical professionals.
- There is a need for a transparent, explainable TB detection system that validates model attention against clinically significant lung regions.

## SLIDE: Literary Review

- **Rajpurkar et al. (2017)** developed CheXNet using DenseNet121 trained on the ChestX-ray14 dataset, achieving radiologist-level performance on pneumonia detection but not specifically optimized for TB.
- **Jaeger et al. (2014)** released the Shenzhen and Montgomery TB chest X-ray datasets through the U.S. National Library of Medicine, establishing the standard benchmark for TB classification research.
- **He et al. (2016)** introduced ResNet with skip connections, which has since become one of the most widely adopted CNN architectures in medical imaging and transfer learning.
- **Huang et al. (2017)** proposed DenseNet with dense connectivity between layers, improving feature reuse and gradient flow — beneficial for detecting subtle patterns in medical images.
- **Selvaraju et al. (2017)** introduced Grad-CAM for visual explanations of CNN predictions, enabling verification of whether models attend to clinically relevant regions.
- **Existing Gap:** Few studies combine binary TB detection with a systematic Grad-CAM analysis comparing whether model attention aligns with radiologist-identified TB regions.

## SLIDE: Objectives

- To compare the classification performance of ResNet50, DenseNet121, and EfficientNet-B0 for binary TB detection using the Shenzhen and Montgomery chest X-ray datasets.
- To evaluate each model using accuracy, sensitivity, specificity, and AUC-ROC to determine diagnostic reliability.
- To generate Grad-CAM heatmaps and validate whether model attention aligns with lung regions using Montgomery's lung segmentation masks.
- To identify which pretrained CNN architecture provides the best combination of detection accuracy and clinically meaningful explainability.
- To deploy the best-performing model as a Next.js web application with a FastAPI backend for accessible TB screening.

## SLIDE: Hypothesis

- **H1:** DenseNet121 will achieve the highest classification accuracy due to its dense connectivity promoting feature reuse, which is beneficial for detecting subtle TB patterns.
- **H2:** ResNet50 will serve as a strong baseline with competitive performance, consistent with its widespread use in medical imaging literature.
- **H3:** EfficientNet-B0 will achieve comparable accuracy to DenseNet121 while being the most computationally efficient among the three models.
- **H4:** Grad-CAM heatmaps from all three models will primarily highlight upper lung regions, consistent with where TB abnormalities typically appear, with higher-accuracy models showing better alignment with lung segmentation masks.

## SLIDE: Methodology

- **Dataset:** Shenzhen (662 images) and Montgomery (138 images) chest X-ray datasets for binary TB classification (800 total), with Montgomery providing lung segmentation masks for Grad-CAM validation.
- **Preprocessing:** Image resizing, normalization, and data augmentation (rotation, flipping, zooming, brightness adjustment) to address the small dataset size and improve generalization.
- **Model Training:** Fine-tune three pretrained CNNs — ResNet50, DenseNet121, and EfficientNet-B0 — using transfer learning from ImageNet weights on Google Colab.
- **Evaluation Metrics:** Accuracy, sensitivity, specificity, and AUC-ROC for classification performance.
- **Explainability:** Generate Grad-CAM heatmaps and measure alignment with Montgomery's lung segmentation masks using IoU (Intersection over Union).
- **Deployment:** Deploy the best model as a web application using Next.js (frontend) and FastAPI (Python backend).

## SLIDE: Expected Outcomes

- A comparative performance table of ResNet50, DenseNet121, and EfficientNet-B0 evaluated on accuracy, sensitivity, specificity, and AUC-ROC.
- Grad-CAM heatmap visualizations showing model attention for TB-positive and normal cases across all three architectures.
- Quantitative IoU analysis measuring how well each model's Grad-CAM attention aligns with radiologist-drawn lung segmentation masks.
- Identification of the best CNN architecture for both detection accuracy and clinically meaningful explainability.
- A working Next.js + FastAPI web application prototype for TB screening.

## SLIDE: Recommendations

- Future studies may expand the dataset by incorporating larger chest X-ray collections (e.g., ChestX-ray14) to improve model generalization.
- Conduct clinical validation with radiologists to evaluate whether Grad-CAM explanations are useful in real diagnostic workflows.
- Extend the system to detect additional lung conditions beyond TB (e.g., pneumonia, lung nodules) for broader clinical utility.
- Explore the use of lung segmentation as a preprocessing step to force models to focus only on lung regions before classification.
- Investigate the system's performance on Filipino patient X-rays to assess local applicability, as current datasets are from China and the USA.
- Integrate the web application with hospital information systems for seamless adoption in Philippine healthcare facilities.

---

# TOPIC 3: Deepfake Face Detection — CNN Performance on Compressed Social Media Images

---

## SLIDE: Introduction

- Deepfake technology has made it increasingly easy to create convincing face-swapped images and videos, posing serious threats to information integrity and public trust.
- Social media platforms like Facebook, Instagram, and Twitter apply heavy JPEG compression to uploaded images, which destroys the subtle artifacts that deepfake detectors rely on.
- Most existing detection studies report accuracy on uncompressed or lightly compressed data, which does not reflect real-world social media conditions.
- This study evaluates three CNN architectures — XceptionNet, EfficientNet-B4, and ResNet50 — on a combined FaceForensics++ and Celeb-DF dataset across multiple JPEG compression levels (c0, c23, c40).
- Aligned with **SDG 16: Peace, Justice and Strong Institutions** — combating misinformation and digital manipulation.

## SLIDE: Problem Statement

- The rise of AI-generated deepfakes threatens democratic processes, personal reputations, and public discourse, especially when spread through social media.
- Social media platforms compress uploaded images (JPEG quality c40), destroying subtle forgery artifacts that detection models depend on to distinguish real from fake.
- Most deepfake detection research evaluates models on raw or lightly compressed images (c0, c23), creating a gap between reported benchmark accuracy and real-world performance.
- There is a need to systematically measure how compression degrades detection accuracy and identify which CNN architecture is most robust under real-world social media conditions.

## SLIDE: Literary Review

- **Rossler et al. (2019)** introduced the FaceForensics++ benchmark with four deepfake manipulation methods (Face2Face, FaceSwap, DeepFakes, NeuralTextures) and established XceptionNet as the standard baseline detector.
- **Li et al. (2020)** introduced the Celeb-DF dataset featuring celebrity deepfake videos with improved visual quality, providing a more challenging benchmark for detection.
- **Chollet (2017)** proposed XceptionNet using depthwise separable convolutions for image classification, which was later adopted as the standard architecture for deepfake detection by Rossler et al. (2019).
- **Zhang et al. (2016)** developed MTCNN (Multi-Task Cascaded Convolutional Network) for face detection and alignment, widely used as a preprocessing step in deepfake detection pipelines.
- **Tan & Le (2019)** developed EfficientNet using compound scaling to balance depth, width, and resolution, with B4 variant offering strong accuracy-efficiency balance.
- **Existing Gap:** Few studies systematically measure how JPEG compression at social media levels (c40) degrades detection accuracy across different CNN architectures.

## SLIDE: Objectives

- To evaluate the deepfake detection performance of XceptionNet, EfficientNet-B4, and ResNet50 on a combined FaceForensics++ and Celeb-DF dataset.
- To measure classification accuracy, AUC-ROC, and F1-score at three JPEG compression levels: c0 (raw), c23 (light), and c40 (heavy/social media).
- To quantify the accuracy drop from c0 to c40 for each model, identifying which architecture is most robust under compression.
- To use MTCNN for face extraction as a preprocessing step to ensure consistent face-cropped input across all models.
- To deploy the most robust model as a Next.js web application for real-world deepfake detection.

## SLIDE: Hypothesis

- **H1:** XceptionNet will achieve the highest accuracy on raw images (c0) as it is the established benchmark architecture for deepfake detection.
- **H2:** EfficientNet-B4 will be the most robust model under heavy compression (c40), experiencing the smallest accuracy drop from c0 to c40 due to its compound scaling approach.
- **H3:** ResNet50 will show the largest accuracy degradation under compression, as it is a general-purpose architecture not specialized for forgery detection.
- **H4:** All three models will experience significant accuracy drops (>10%) when moving from raw (c0) to heavy compression (c40), confirming that compression is a critical challenge for real-world deployment.

## SLIDE: Methodology

- **Dataset:** Combined FaceForensics++ and Celeb-DF dataset (400 videos, ~16,000 face-cropped frames) tested at three JPEG compression levels: c0, c23, and c40.
- **Face Extraction:** MTCNN is used to detect and crop faces from video frames as a preprocessing step before classification.
- **Model Training:** Fine-tune three pretrained CNNs — XceptionNet, EfficientNet-B4, and ResNet50 — using transfer learning from ImageNet weights on Google Colab.
- **Compression Testing:** Each model is evaluated separately at c0 (raw), c23 (light), and c40 (heavy) to measure performance degradation across compression levels.
- **Evaluation Metrics:** Accuracy, AUC-ROC, and F1-score at each compression level, plus accuracy drop measurement from c0 to c40.
- **Deployment:** Deploy the most robust model as a Next.js web application where users can upload images for real/fake classification with confidence scores.

## SLIDE: Expected Outcomes

- A comparative performance table showing accuracy, AUC-ROC, and F1-score for all three models at each compression level (c0, c23, c40).
- A clear measurement of accuracy drop from c0 to c40 for each architecture, identifying the most compression-robust model.
- Cross-dataset generalization results showing how models trained on combined FF++ and Celeb-DF data perform on each dataset individually.
- Identification of the best CNN architecture for real-world deepfake detection under social media compression conditions.
- A working Next.js web application prototype for deepfake face detection.

## SLIDE: Recommendations

- Future studies may incorporate additional compression formats beyond JPEG, such as WebP and HEIC, which are increasingly used by modern social media platforms.
- Explore video-level detection using temporal analysis (frame-to-frame inconsistencies) in addition to single-frame image classification.
- Investigate adversarial robustness — testing whether models can withstand deepfakes specifically designed to evade detection.
- Extend the dataset to include newer deepfake generation methods (e.g., diffusion-based models) that may produce different artifacts.
- Evaluate the system's performance on deepfakes of Filipino faces, as current datasets are predominantly Western celebrities.
- Integrate the detection tool with social media platform APIs for automated screening of uploaded content.

---

# TOPIC 4: Post-Disaster Building Damage Assessment — CNN vs Vision Transformer

---

## SLIDE: Introduction

- Rapid post-disaster damage assessment is critical for emergency response, yet manual inspection of satellite imagery is slow and labor-intensive.
- The Philippines is one of the most disaster-prone countries in the world, experiencing destructive typhoons annually that cause widespread building damage.
- Deep learning models, particularly CNNs and Vision Transformers, offer potential for automated building damage classification from satellite imagery.
- This study compares three architectures — ResNet50, EfficientNet-B0, and Vision Transformer (ViT-Small) — for binary damage classification (damaged vs. undamaged), with Grad-CAM used to verify that models focus on actual structural damage.
- Aligned with **SDG 11: Sustainable Cities and Communities** — accelerating disaster response through automated damage assessment.

## SLIDE: Problem Statement

- After a disaster, assessing building damage across large areas using satellite imagery requires significant manual effort and time, delaying emergency response.
- CNNs have been applied to damage assessment, but few studies compare CNN architectures against Vision Transformers, which capture global context through self-attention — potentially better suited for understanding overall structural damage.
- Most existing models operate as black boxes, providing damage predictions without explaining which image regions influenced the decision, reducing trust among disaster responders.
- There is a need for a transparent, explainable damage classification system that compares CNN and Transformer approaches and validates model attention on actual structural damage indicators.

## SLIDE: Literary Review

- **Dosovitskiy et al. (2021)** introduced the Vision Transformer (ViT), demonstrating that a pure transformer architecture applied to image patches can achieve competitive performance with CNNs on image classification tasks.
- **Gupta et al. (2019)** introduced the xBD dataset and benchmark for building damage assessment from satellite imagery, establishing the standard evaluation framework for post-disaster damage classification.
- **He et al. (2016)** introduced ResNet with skip connections, which has since become one of the most widely adopted CNN architectures in computer vision and transfer learning applications.
- **Tan & Le (2019)** developed EfficientNet using compound scaling to balance depth, width, and resolution, achieving strong accuracy with fewer parameters.
- **Selvaraju et al. (2017)** introduced Grad-CAM for visual explanations of CNN predictions, enabling verification of whether models attend to relevant image regions.
- **Existing Gap:** Few studies compare CNN vs. Vision Transformer performance on satellite-based building damage assessment, and fewer incorporate Grad-CAM to verify whether models focus on actual structural damage indicators.

## SLIDE: Objectives

- To compare the classification performance of ResNet50, EfficientNet-B0, and ViT-Small for binary building damage detection from post-hurricane satellite imagery.
- To evaluate whether Vision Transformer's global attention mechanism outperforms CNN's local feature extraction for satellite damage classification.
- To generate Grad-CAM heatmaps and verify whether models focus on actual structural damage indicators (collapsed roofs, debris) rather than irrelevant features (trees, roads).
- To measure each model using accuracy, F1-score, sensitivity, specificity, and AUC-ROC.
- To deploy the best-performing model as a Next.js web dashboard for satellite image upload and damage classification.

## SLIDE: Hypothesis

- **H1:** ViT-Small will achieve the highest classification accuracy due to its global self-attention mechanism, which can capture overall structural damage patterns across the entire satellite image.
- **H2:** EfficientNet-B0 will provide competitive accuracy to ResNet50 while being significantly smaller in model size, demonstrating the effectiveness of compound scaling for satellite imagery.
- **H3:** ResNet50 will serve as a strong baseline but may be outperformed by ViT-Small on images where global context (entire building collapse) is more informative than local textures.
- **H4:** Grad-CAM heatmaps from ViT-Small will show broader attention across building structures, while CNN models will focus on localized damage features such as roof damage and debris.

## SLIDE: Methodology

- **Dataset:** Satellite Images of Hurricane Damage dataset from Kaggle (66 MB, binary classification: damaged vs. undamaged building patches).
- **Preprocessing:** Image resizing, normalization, and data augmentation (rotation, flipping, color jittering) to improve model generalization with the limited dataset size.
- **Model Training:** Fine-tune three pretrained architectures — ResNet50, EfficientNet-B0, and ViT-Small — using transfer learning from ImageNet weights on Google Colab.
- **Evaluation Metrics:** Accuracy, F1-score, sensitivity, specificity, AUC-ROC, and confusion matrix for comprehensive performance comparison.
- **Explainability:** Generate Grad-CAM heatmaps to visualize model attention and qualitatively verify focus on structural damage indicators versus background features.
- **Deployment:** Deploy the best-performing model as a Next.js web dashboard where users can upload satellite images for damage classification with visual explanations.

## SLIDE: Expected Outcomes

- A comparative performance table of ResNet50, EfficientNet-B0, and ViT-Small evaluated on accuracy, F1-score, sensitivity, specificity, and AUC-ROC.
- A clear assessment of whether Vision Transformer's global attention outperforms CNN's local feature extraction for satellite damage classification.
- Grad-CAM heatmap visualizations demonstrating model attention patterns, comparing how CNNs and ViT attend to damage regions differently.
- Identification of the best architecture for post-disaster building damage classification from satellite imagery.
- A working Next.js web dashboard prototype for satellite image upload and damage classification.

## SLIDE: Recommendations

- Future studies may validate the model on Philippine typhoon imagery (e.g., Typhoon Haiyan datasets) to assess local applicability beyond hurricane damage.
- Explore multi-class damage classification (minor, major, destroyed) instead of binary classification for more granular damage assessment.
- Incorporate pre-disaster and post-disaster image pairs (change detection) to improve classification accuracy by comparing before-and-after conditions.
- Investigate the use of larger satellite imagery datasets such as xBD for improved model generalization across different disaster types and geographic regions.
- Integrate the web dashboard with Geographic Information Systems (GIS) for spatial mapping of damage assessments across affected areas.
- Explore real-time deployment on edge devices for field-based damage assessment by disaster response teams.

---

# TOPIC 5: AI-Generated Text Detection — Machine Learning vs Transformers

---

## SLIDE: Introduction

- The rise of Large Language Models (LLMs) such as GPT-3.5 and GPT-4 has made AI-generated text increasingly difficult to distinguish from human writing.
- This poses a significant threat to academic integrity, as students can easily produce AI-written essays and assignments that are hard to detect.
- While commercial tools like GPTZero and Turnitin AI Detection exist, they operate as black boxes with unpublished methodologies, limiting transparency and reproducibility.
- This study compares traditional ML approaches (TF-IDF with Logistic Regression, SVM, and Random Forest) against fine-tuned Transformer models (DistilBERT, RoBERTa) for binary AI-generated text detection.
- Aligned with **SDG 4: Quality Education** — providing educators with a transparent, reproducible tool to support academic integrity.

## SLIDE: Problem Statement

- AI-generated text from LLMs is becoming nearly indistinguishable from human writing, creating a growing challenge for academic institutions worldwide.
- Existing commercial AI detection tools are proprietary and lack transparent, reproducible methodologies, making them unsuitable for academic research and verification.
- It remains unclear whether expensive Transformer-based models are necessary for effective detection, or if traditional ML approaches can achieve comparable results at significantly lower computational cost.
- There is a need for an open, reproducible comparison of traditional ML vs. Transformer approaches that provides cost-aware recommendations for educational institutions with varying resource levels.

## SLIDE: Literary Review

- **Devlin et al. (2019)** introduced BERT, establishing the pretrain-then-fine-tune paradigm for NLP tasks, which forms the foundation for Transformer-based text classification approaches.
- **Liu et al. (2019)** introduced RoBERTa, trained on 160GB of text with improved training methodology, achieving state-of-the-art results on multiple NLP benchmarks.
- **Sanh et al. (2019)** introduced DistilBERT, a distilled version of BERT that retains 97% of its language understanding while being 60% faster and 40% smaller.
- **Mitchell et al. (2023)** proposed DetectGPT, a zero-shot AI-generated text detection method using probability curvature, demonstrating that LLM-generated text occupies distinct regions in a model's log-probability space.
- **Cortes & Vapnik (1995)** introduced Support Vector Machines, which remain a strong baseline for text classification tasks when combined with TF-IDF feature extraction.
- **Existing Gap:** Few peer-reviewed studies systematically compare traditional ML vs. Transformer-based approaches for AI text detection with transparent, reproducible methodology and cost-benefit analysis.

## SLIDE: Objectives

- To compare the detection performance of traditional ML models (TF-IDF + Logistic Regression, SVM, Random Forest) against fine-tuned Transformers (DistilBERT, RoBERTa) for binary AI-generated text classification.
- To evaluate each model using accuracy, F1-score, AUC-ROC, precision, and recall on the AI vs Human Text dataset (500,000 essays).
- To measure inference speed and computational cost for each approach, determining the practical tradeoff between accuracy and efficiency.
- To provide cost-aware recommendations for educational institutions with varying resource levels (no budget vs. GPU-equipped).
- To deploy the best-performing model as a Next.js web application where users can submit text and receive a classification with a confidence score.

## SLIDE: Hypothesis

- **H1:** RoBERTa will achieve the highest detection accuracy (~93–95%) due to its extensive pretraining on 160GB of text, giving it the strongest language understanding capabilities.
- **H2:** DistilBERT will achieve accuracy within 2–3% of RoBERTa while being significantly faster, offering the best accuracy-to-speed tradeoff among Transformer models.
- **H3:** TF-IDF + SVM will be the strongest traditional ML approach, achieving ~85–90% accuracy at a fraction of the computational cost and inference time of Transformers.
- **H4:** The accuracy gap between the best traditional ML model and the best Transformer will be less than 10%, suggesting that traditional ML may be "good enough" for resource-constrained educational settings.

## SLIDE: Methodology

- **Dataset:** AI vs Human Text dataset from Kaggle (500,000 essays, binary classification: AI-generated vs. human-written, 367 MB).
- **Text Preprocessing:** Tokenization, text length extraction, vocabulary richness calculation, and perplexity scoring as linguistic features for the ML pipeline.
- **Traditional ML Pipeline:** Extract TF-IDF features from preprocessed text, then train three classifiers — Logistic Regression, SVM, and Random Forest — using scikit-learn.
- **Transformer Pipeline:** Fine-tune DistilBERT and RoBERTa on the dataset using Hugging Face Transformers on Google Colab with GPU.
- **Evaluation Metrics:** Accuracy, F1-score, AUC-ROC, precision, recall, confusion matrix, inference time (ms per prediction), and hardware requirements.
- **Deployment:** Deploy the best model as a Next.js web application where users can paste text and receive a classification with a confidence score.

## SLIDE: Expected Outcomes

- A comparative performance table of all five models (TF-IDF + LR, SVM, RF, DistilBERT, RoBERTa) evaluated on accuracy, F1-score, AUC-ROC, precision, and recall.
- An inference speed and cost comparison showing the practical tradeoff between traditional ML (milliseconds, no GPU) and Transformers (slower, GPU required).
- A cost-benefit analysis providing tiered recommendations: budget-friendly (TF-IDF), mid-range (DistilBERT), and high-accuracy (RoBERTa) options for schools.
- Identification of the best overall model considering both accuracy and practical deployment constraints.
- A working Next.js web application prototype for AI-generated text detection with confidence scores.

## SLIDE: Recommendations

- Future studies may extend the detection system to support non-English text, particularly Filipino and Taglish, using multilingual Transformer models (mBERT, XLM-RoBERTa).
- Investigate paragraph-level and sentence-level detection to handle mixed human/AI-assisted writing, which the current binary approach does not address.
- Continuously update the training dataset to include text from newer LLMs (GPT-5, Claude, Gemini) as the AI text generation landscape evolves.
- Explore ensemble methods combining TF-IDF features with Transformer embeddings for potentially improved detection accuracy.
- Prioritize minimizing false positives (falsely accusing students of AI use) through threshold tuning and confidence-based rather than binary classification outputs.
- Collaborate with educational institutions in the Philippines for real-world pilot testing and validation of the detection tool in academic settings.

---

## SLIDE: Conclusion

- All five topics address real-world problems aligned with UN Sustainable Development Goals (SDG 3, 4, 11, 16), covering both Computer Vision and Natural Language Processing.
- Each topic follows a systematic approach: identified research gap, model comparison methodology, and an explainability or evaluation component.
- All studies are feasible within one academic year using publicly available datasets and Google Colab, with each producing a deployable prototype (Flutter app or Next.js web app).
- The group welcomes the panel's feedback and recommendation on which topic best fits the program's direction.

---

## SLIDE: Thank You

- Thank you for your time and consideration.
- We welcome your questions, comments, and recommendations.
