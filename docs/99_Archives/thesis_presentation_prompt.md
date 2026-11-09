# Thesis Topics Presentation Prompt

Copy the prompt below and use it with Claude's canvas-design skill to generate a multi-page PDF presentation.

---

## PROMPT (Copy Everything Below This Line)

```
Create a multi-page presentation design (PDF, 7-8 pages) for a BSCS Thesis Topic Proposal. This will be presented to academic advisors/panel for topic selection.

**PRESENTATION STRUCTURE:**

**Page 1 — Cover**
- Title: "Proposed BSCS Thesis Topics"
- Subtitle: "AI & Machine Learning Research Proposals"
- Focus areas: Computer Vision · NLP · Transfer Learning
- Context: 5 thesis topics aligned with UN Sustainable Development Goals

**Page 2 — Topic 1: Skin Lesion Classification (SDG 3: Health)**
- Research Title: "Lightweight CNN Comparison for Mobile Skin Lesion Detection with Explainability"
- Models compared: MobileNetV3 vs EfficientNet-Lite vs ShuffleNet
- Dataset: HAM10000 (10,015 dermoscopic images, 7 diagnostic classes)
- Tech stack: Grad-CAM · TensorFlow Lite · Flutter mobile app
- Research question: "Which lightweight architecture provides the best accuracy-to-efficiency tradeoff for on-device skin lesion classification?"
- Deployment: Mobile phone (offline inference)

**Page 3 — Topic 2: Tuberculosis X-Ray Detection (SDG 3: Health)**
- Research Title: "Transfer Learning-Based TB Detection with Grad-CAM Validation Against Radiologist Annotations"
- Models compared: ResNet50 vs DenseNet121 vs EfficientNet-B0
- Dataset: Shenzhen + Montgomery (800 chest X-rays, binary classification)
- Key innovation: Validate if Grad-CAM attention aligns with radiologist-identified TB regions
- Tech stack: Grad-CAM · Next.js · FastAPI
- Deployment: Web application

**Page 4 — Topic 3: Deepfake Face Detection (SDG 16: Justice)**
- Research Title: "Compression-Aware Deepfake Detection for Social Media Conditions"
- Models compared: XceptionNet vs EfficientNet-B4 vs ResNet50
- Dataset: FaceForensics++ & Celeb-DF (16,000 face frames)
- Key innovation: Test detection accuracy across JPEG compression levels (c0 → c23 → c40)
- Research question: "How does social media compression degrade deepfake detection accuracy?"
- Deployment: Web application

**Page 5 — Topic 4: Disaster Building Damage Assessment (SDG 11: Cities)**
- Research Title: "CNN vs Vision Transformer for Satellite Building Damage Classification"
- Models compared: ResNet50 vs EfficientNet-B0 vs ViT-Small
- Dataset: Hurricane Satellite Damage (66 MB, binary: damaged/undamaged)
- Key innovation: Compare CNN (local patterns) vs Vision Transformer (global attention)
- Research question: "Does global context (ViT) beat local patterns (CNN) for satellite damage detection?"
- Relevance: Philippine typhoon disaster response
- Deployment: Web dashboard

**Page 6 — Topic 5: AI-Generated Text Detection (SDG 4: Education)**
- Research Title: "Traditional ML vs Transformers for AI-Generated Text Detection"
- Models compared: TF-IDF + (Logistic Regression, SVM, Random Forest) vs DistilBERT vs RoBERTa
- Dataset: AI vs Human Text (500,000 essays, binary classification)
- Key innovation: Compare WITH vs WITHOUT transfer learning — is expensive transformer worth it?
- Research question: "Can cheap TF-IDF compete with expensive transformers for AI text detection?"
- Relevance: Academic integrity in schools
- Deployment: Web application

**Page 7 — Comparison Summary**
Visual comparison table of all 5 topics:
| Topic | SDG | Domain | Models | Dataset Size | Deployment |
| Skin Lesion | SDG 3 | Computer Vision | 3 lightweight CNNs | 10,015 images | Mobile |
| TB Detection | SDG 3 | Computer Vision | 3 standard CNNs | 800 X-rays | Web |
| Deepfake | SDG 16 | Computer Vision | 3 CNNs | 16,000 frames | Web |
| Disaster | SDG 11 | Computer Vision | 2 CNNs + 1 ViT | 66 MB | Web |
| AI Text | SDG 4 | NLP | 3 Traditional + 2 Transformer | 500K essays | Web |

**DESIGN DIRECTION:**
- **Aesthetic**: Academic, professional, clean — suitable for thesis proposal/defense
- **Style**: Modern minimalist with breathing room — information should be scannable at a glance
- **Visual elements**: Use simple icons/graphics for SDGs, model architectures, and tech stack
- **Color palette**: Professional and cohesive — deep blues, teals, or academic tones
- **Typography**: Clean sans-serif, strong visual hierarchy (title → subtitle → body)
- **Layout**: Each topic page should have consistent structure for easy comparison
- **Feel**: Technical but accessible — this is Computer Science research, not marketing

**CRITICAL REQUIREMENTS:**
- Multi-page PDF (7-8 pages total)
- Each page should be a complete visual composition
- Minimal text, maximum visual communication
- Information hierarchy should be instantly clear
- Professional enough for academic presentation

**OUTPUT**: Multi-page PDF, design-forward, ready for thesis proposal presentation
```

---

## How to Use

1. Open Claude with the **canvas-design** skill enabled
2. Copy the entire prompt above (everything inside the code block)
3. Paste it into Claude
4. Claude will generate a multi-page PDF presentation

## Notes

- This prompt is based on the 5 thesis topics from `5_Possible_Topics.md`
- All technical details (models, datasets, research questions) are accurate to the source
- The design direction is tailored for academic presentation contexts
