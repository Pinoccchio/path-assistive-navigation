# Thesis Topic Proposal Template

A comprehensive guide for BSCS students to structure and write thesis topic proposals.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Format Overview](#format-overview)
3. [Blank Template](#blank-template)
4. [Complete Examples](#complete-examples)
5. [Writing Tips](#writing-tips)
6. [SDG Reference List](#sdg-reference-list)
7. [Recommended Dataset Sources](#recommended-dataset-sources)

---

## Introduction

### What is this document?

This template provides a standardized format for writing thesis topic proposals. It includes:
- A clear structure that covers all required elements
- Placeholder markers to guide your writing
- Complete examples using generic topics (including a model comparison study)
- Tips for writing compelling proposals

### How to use this document

1. **Read the Format Overview** to understand what each section requires
2. **Copy the Blank Template** as your starting point
3. **Review the Example** to see how a complete proposal looks
4. **Apply the Writing Tips** to strengthen your proposal
5. **Use the SDG and Dataset references** to support your choices

---

## Format Overview

| Section | Purpose | Key Questions to Answer |
|---------|---------|------------------------|
| **Title** | Full descriptive title in blockquote format | What technique? What domain? What's the contribution? |
| **Overview** | Comprehensive paragraph covering the full scope | Problem → Approach → Dataset → Evaluation → Deployment |
| **SDG Alignment** | Connect to UN Sustainable Development Goals | Which SDG? Who benefits? How does your work contribute directly? |
| **CS Domain** | Classify technical areas (use `·` separator) | Computer Vision? NLP? Transfer Learning? Mobile Deployment? |
| **Key Technologies** | Table format with Category/Details columns | Models compared, frameworks, training environment, deployment, metrics |
| **Research Gap** | Justify why this matters + explicit research question | What's missing? End with: *"This study investigates: [question]?"* |
| **Dataset** | Table format with Source/Description + hyperlinks | Dataset name, platform, size, classes, accessibility |

---

## Blank Template

Copy everything below this line and fill in your own content:

---

```
## Topic [NUMBER] — [SHORT TOPIC NAME]

**SDG [NUMBER]: [SDG NAME]**

### Title

> [Your full descriptive title here — be specific about the technique, domain, and contribution]

### Overview

[Write a comprehensive paragraph describing:
- The real-world problem and its significance
- Your proposed technical approach (models, methods)
- The dataset you'll use
- How you'll evaluate/compare results
- The deployment/output format]

### SDG Alignment

Addresses **SDG [NUMBER] ([SDG NAME])** by [explain the direct connection between your technical work and the SDG target. Be specific about who benefits and how.]

### CS Domain

[Domain 1] · [Domain 2] · [Domain 3]

(Examples: Computer Vision · Transfer Learning · Mobile ML Deployment)

### Key Technologies

| Category | Details |
|---|---|
| Models | [List specific models to compare, e.g., ResNet50, EfficientNet-B0, ViT-Small] |
| Explainability | [If applicable: Grad-CAM, SHAP, LIME, etc.] |
| Training Environment | [e.g., Python, TensorFlow/Keras, Google Colab] |
| Deployment | [e.g., Next.js (web), Flutter (mobile), FastAPI (backend)] |
| Evaluation Metrics | [e.g., Accuracy, F1-score, AUC-ROC, Inference time, Model size] |

### Research Gap

[Explain what's missing in current solutions. Be specific about the limitations of existing work. Then end with your specific research question in italics:]

*This study investigates: [Your specific research question here?]*

### Dataset

| Source | Description |
|---|---|
| [Dataset Name (Platform)](URL) | [Brief description: number of samples, classes, file size] |
| [Additional Dataset (Platform)](URL) | [Description — mark as "supplementary" if applicable] |
```

---

## Complete Examples

Below are complete examples using **generic, well-established topics**. These demonstrate the format only — you should develop your own original ideas.

---

### Example 1 — Sentiment Analysis of Product Reviews

**SDG 9: Industry, Innovation and Infrastructure**

#### Title

> A Comparative Analysis of LSTM and Transformer Models for Multi-Domain Product Review Sentiment Classification

#### Overview

Online shoppers rely heavily on product reviews, but reading hundreds of reviews is time-consuming and inconsistent. This study compares traditional deep learning approaches (LSTM, BiLSTM with Attention) against transformer-based models (DistilBERT, RoBERTa) for ternary sentiment classification (positive, negative, neutral) on the Amazon Product Reviews dataset. The key research angle is evaluating **cross-domain generalization** — training on one product category (e.g., Electronics) and testing on others (e.g., Books, Clothing) to assess model robustness. A preprocessing pipeline handles text cleaning, tokenization, and class balancing. The best model will be deployed as a Next.js web application where users can paste review text and receive sentiment predictions with confidence scores.

#### SDG Alignment

Addresses **SDG 9 (Industry, Innovation and Infrastructure)** by providing automated tools that improve the efficiency of online marketplaces. Better sentiment analysis helps businesses respond to customer needs faster and enables consumers to make informed purchasing decisions — promoting sustainable digital commerce infrastructure.

#### CS Domain

Natural Language Processing · Deep Learning · Transfer Learning

#### Key Technologies

| Category | Details |
|---|---|
| Traditional DL Models | LSTM, BiLSTM with Attention Mechanism |
| Transformer Models | DistilBERT, RoBERTa (fine-tuned) |
| Training Environment | Python, TensorFlow/Keras, Hugging Face Transformers, Google Colab |
| Preprocessing | NLTK, text cleaning, tokenization, SMOTE for class balancing |
| Deployment | Next.js (web application) |
| Evaluation Metrics | Accuracy, F1-score (macro), Precision, Recall, Cross-domain accuracy |

#### Research Gap

While sentiment analysis is a well-studied field, most existing models are evaluated **only within the same domain** they were trained on. Real-world applications require models that generalize across product categories without retraining. Additionally, few studies provide a direct comparison between traditional RNN-based approaches and modern transformers specifically for **cross-domain sentiment transfer**.

*This study investigates: How do LSTM-based models compare to fine-tuned transformers in terms of cross-domain generalization for product review sentiment classification?*

#### Dataset

| Source | Description |
|---|---|
| [Amazon Product Reviews (Kaggle)](https://www.kaggle.com/datasets/snap/amazon-fine-food-reviews) | 500,000+ reviews with star ratings across multiple product categories |
| [Multi-Domain Sentiment Dataset (Kaggle)](https://www.kaggle.com/datasets/jeromeblanchet/multidomain-sentiment-analysis-dataset) | Reviews from 4 domains: Books, DVDs, Electronics, Kitchen (supplementary) |

---

### Example 2 — Filipino Sign Language Recognition

**SDG 10: Reduced Inequalities**

*This example demonstrates a **model comparison study**, which is a common and valid thesis approach.*

#### Title

> A Comparative Analysis of CNN Architectures for Real-Time Filipino Sign Language Alphabet Recognition with Mobile Deployment

#### Overview

Approximately 1.8 million Filipinos are deaf or hard of hearing, yet Filipino Sign Language (FSL) interpreters are scarce. This study compares four CNN architectures — a custom baseline CNN, VGG16, ResNet50, and MobileNetV2 — for real-time FSL alphabet recognition (28 classes including Ñ and NG). The models are evaluated not only on classification accuracy but also on **deployment feasibility metrics**: inference time, model size, and frames-per-second on mobile devices. Hand regions are extracted using MediaPipe prior to classification. Data augmentation (rotation, brightness, flipping) addresses dataset limitations. The best-performing model will be converted to TensorFlow Lite and deployed on a Flutter mobile application for real-time camera-based recognition.

#### SDG Alignment

Addresses **SDG 10 (Reduced Inequalities)** by creating accessible technology for the deaf and hard-of-hearing community in the Philippines. The system reduces communication barriers in education, employment, and daily interactions — promoting social inclusion for persons with disabilities.

#### CS Domain

Computer Vision · Deep Learning · Transfer Learning · Mobile ML Deployment

#### Key Technologies

| Category | Details |
|---|---|
| Models | Custom CNN (baseline), VGG16, ResNet50, MobileNetV2 (all pretrained on ImageNet except baseline) |
| Hand Detection | MediaPipe Hands for region extraction |
| Training Environment | Python, TensorFlow/Keras, Google Colab |
| Data Augmentation | Rotation, brightness adjustment, horizontal flip, zoom |
| Deployment | TensorFlow Lite, Flutter (Android/iOS) |
| Evaluation Metrics | Accuracy, F1-score (macro), Inference time (ms), Model size (MB), FPS on mobile |

#### Research Gap

While sign language recognition has been extensively studied for American Sign Language (ASL), Filipino Sign Language remains underrepresented in research despite having distinct signs and gestures. Existing FSL studies typically: (1) recognize only a subset of the alphabet (10-15 letters), (2) implement a single model without benchmarking alternatives, and (3) ignore deployment constraints like model size and inference speed.

*This study investigates: Which CNN architecture provides the optimal accuracy-to-efficiency tradeoff for real-time FSL alphabet recognition on mobile devices?*

#### Dataset

| Source | Description |
|---|---|
| [Filipino Sign Language Dataset (Kaggle)](https://www.kaggle.com/datasets/jamesnogra/filipino-sign-language) | FSL alphabet images, multiple signers |
| Self-collected Dataset | 1,000+ images per class from volunteer signers with varying backgrounds/lighting (to be made publicly available) |

---

## Writing Tips

### The "So What?" Test

Your research gap is the most critical section. After writing it, ask yourself:

> "So what? Why should anyone care about this?"

**Weak Research Gap:**
> "This research will classify images using CNN."

*Problem: So what? Many systems already do this.*

**Strong Research Gap:**
> "Existing image classification systems require large labeled datasets (10,000+ images), making them impractical for small businesses or niche applications. This research proposes a few-shot learning approach that achieves comparable accuracy with only 50-100 training images per class, democratizing access to custom image classification."

*Better: Identifies a specific limitation and explains who benefits from solving it.*

### How to Align with SDGs Properly

**Do:**
- Choose 1-2 SDGs maximum (focus is better)
- Explain the *direct* connection between your technical work and the goal
- Be specific about the beneficiaries (students, farmers, patients, etc.)

**Don't:**
- Claim alignment with 5+ SDGs (dilutes your argument)
- Use vague connections ("technology helps everyone")
- Force a connection that doesn't exist

**Example of Forced Connection (Avoid):**
> "SDG 16 - Peace and Justice: Our recipe recommendation app promotes peace by bringing families together at dinner."

**Example of Genuine Connection:**
> "SDG 3 - Good Health: Our recipe recommendation app helps users with diabetes find meal options that meet their dietary restrictions, directly supporting disease management."

### Choosing Evaluation Metrics

Match your metrics to your problem type:

| Problem Type | Common Metrics |
|--------------|----------------|
| Classification | Accuracy, Precision, Recall, F1-Score, AUC-ROC |
| Regression | MAE, MSE, RMSE, R-squared |
| Object Detection | mAP, IoU |
| NLP Generation | BLEU, ROUGE, Perplexity |
| Recommendation | Precision@K, Recall@K, NDCG |
| Clustering | Silhouette Score, Davies-Bouldin Index |

**Tip:** Always include multiple metrics. Accuracy alone can be misleading for imbalanced datasets.

### Common Mistakes to Avoid

| Mistake | Why It's a Problem | How to Fix |
|---------|-------------------|------------|
| Too broad title | "AI for Healthcare" - what specifically? | Narrow down: "Pneumonia Detection from Chest X-rays Using CNN" |
| No clear problem | Jumping to solution without establishing need | Start with the problem users face |
| Outdated techniques | Proposing methods from 10+ years ago | Review recent papers (2022-2024) in your domain |
| Unavailable data | Planning to use proprietary or restricted data | Verify dataset access BEFORE committing to topic |
| Scope creep | Promising to solve everything | Focus on ONE specific contribution |
| No baseline | Can't measure improvement without comparison | Identify existing solutions to compare against |

---

## SDG Reference List

The most relevant SDGs for Computer Science thesis topics:

| SDG | Name | CS Research Applications |
|-----|------|-------------------------|
| **SDG 3** | Good Health and Well-being | Medical diagnosis systems, health monitoring apps, mental health chatbots, drug discovery |
| **SDG 4** | Quality Education | E-learning platforms, intelligent tutoring systems, educational games, accessibility tools |
| **SDG 8** | Decent Work and Economic Growth | Job matching systems, productivity tools, freelance platforms, skills assessment |
| **SDG 9** | Industry, Innovation and Infrastructure | Automation systems, smart manufacturing, infrastructure monitoring, digital transformation |
| **SDG 11** | Sustainable Cities and Communities | Traffic optimization, smart parking, urban planning tools, disaster response systems |
| **SDG 12** | Responsible Consumption and Production | Waste classification, supply chain optimization, sustainable shopping assistants |
| **SDG 13** | Climate Action | Carbon footprint calculators, climate modeling, environmental monitoring, energy optimization |
| **SDG 16** | Peace, Justice and Strong Institutions | Fake news detection, cybersecurity tools, transparency platforms, legal document analysis |

**Tip:** SDGs 3, 4, 9, and 11 are the most commonly aligned with CS research.

---

## Recommended Dataset Sources

### General-Purpose Repositories

| Source | URL | Best For |
|--------|-----|----------|
| **Kaggle** | kaggle.com/datasets | Wide variety, competitions, community kernels |
| **UCI ML Repository** | archive.ics.uci.edu/ml | Classic benchmark datasets |
| **Papers With Code** | paperswithcode.com/datasets | Datasets linked to research papers |
| **Google Dataset Search** | datasetsearch.research.google.com | Searching across multiple sources |
| **Hugging Face Datasets** | huggingface.co/datasets | NLP and text datasets |
| **AWS Open Data** | registry.opendata.aws | Large-scale datasets |

### Domain-Specific Sources

| Domain | Sources |
|--------|---------|
| **Healthcare** | PhysioNet, MIMIC, NIH datasets, Grand Challenges |
| **Computer Vision** | ImageNet, COCO, Open Images, MNIST variants |
| **NLP** | GLUE benchmark, SQuAD, Common Crawl, Wikipedia dumps |
| **Finance** | Yahoo Finance API, Quandl, SEC filings |
| **Agriculture** | PlantVillage, FAO data, crop image datasets |
| **Philippine Data** | PSA OpenSTAT, data.gov.ph, DOST repositories |

### Dataset Evaluation Checklist

Before committing to a dataset, verify:

- [ ] **Accessibility:** Can you actually download/access it?
- [ ] **Size:** Is it large enough for your method? (Deep learning typically needs 1000+ samples)
- [ ] **Quality:** Is it labeled? Are labels accurate?
- [ ] **Relevance:** Does it match your problem domain?
- [ ] **License:** Can you use it for academic research?
- [ ] **Documentation:** Is there a data dictionary or description?
- [ ] **Recency:** Is the data still relevant (especially for social/economic topics)?

---

## Final Checklist

Before submitting your proposal, verify:

- [ ] Title clearly describes the specific research (not too broad, not too narrow)
- [ ] Overview answers: What problem? What solution? What outcome?
- [ ] SDG alignment is genuine and specific (not forced)
- [ ] CS domain is correctly identified
- [ ] Technologies are specific and current (not just "AI" or "Machine Learning")
- [ ] Research gap passes the "So What?" test
- [ ] Dataset is identified AND accessible
- [ ] Scope is achievable in 1 academic year

---

*Template Version 1.0 | Created for BSCS Thesis Preparation*
