from argparse import ArgumentParser
from pathlib import Path
from pptx import Presentation
from pptx.util import Pt

def add_slide(prs, layout_choice, title_text, bullet_points):
    slide_layout = prs.slide_layouts[layout_choice]
    slide = prs.slides.add_slide(slide_layout)
    title = slide.shapes.title
    title.text = title_text
    
    if layout_choice == 1 and bullet_points: # Title and Content
        body_shape = slide.placeholders[1]
        tf = body_shape.text_frame
        tf.clear() # clear existing
        
        for i, point in enumerate(bullet_points):
            p = tf.add_paragraph() if i > 0 else tf.paragraphs[0]
            p.text = point
            p.font.size = Pt(20) # Slightly smaller to fit comprehensive texts
            
            # Sub-bullet check
            if point.startswith("    -"):
                p.level = 2
                p.font.size = Pt(14)
            elif point.startswith("  -"):
                p.level = 1
                p.font.size = Pt(16)
                
    return slide

def generate_presentation(output_path: Path):
    prs = Presentation()
    
    # Title Slide
    slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    
    title.text = "Development and Evaluation of an Offline Mobile-Based Obstacle Detection\nand Distance Estimation System"
    title.text_frame.paragraphs[0].font.size = Pt(36)
    subtitle.text = "RRL Insights & Application Defense\n\nGroup 8 - Assistive Navigation for Visually Impaired\nDivia, Marlan | Guevarra, Jan Miko | Limsan, John Mark"

    # Slide 2
    add_slide(prs, 1, "Scope & Evaluated Literature (2021-2026)", [
        "Objective: To identify critical gaps in global assistive technologies and justify our proposed mobile application framework.",
        "Literature Analyzed: 30 international peer-reviewed papers (2021–2026).",
        "Key Research Benchmarks Included:",
        "  - E. Casanova et al. (2025) [Paper 2]: Systematic Review highlighting 79% of systems remain experimental and require commercial scalability.",
        "  - Prudhvi Naayini et al. (2025) [Paper 1]: Emphasizes the need for robust deployment in diverse, affordable environments."
    ])

    # Slide 3
    add_slide(prs, 1, "Trend 1: Dominance of YOLO for Mobile Edge AI", [
        "Finding: The industry has standardized on YOLO variants (YOLOv8, YOLO-OD) for real-time mobile detection due to high precision-to-speed ratios.",
        "Specific Methodological Evidence:",
        "  - Wang et al. (2024) [Paper 12]: Optimization of YOLOv8 achieved an mAP of 0.88 for walking pace navigation.",
        "  - Okolo et al. (2025) [Paper 4]: Reached 91.7% detection accuracy on a mobile/Raspberry Pi setup.",
        "  - Syed Salman Shah et al. (2026) [Paper 30]: Tensor-RT optimizations proved real-time usability is achievable on edge devices without cloud connectivity.",
        "Our Framework Application: We utilize YOLO models optimized for mobile environments to guarantee sub-25ms detection."
    ])

    # Slide 4
    add_slide(prs, 1, "Trend 2: Shift to AI Monocular Depth Sensing", [
        "Finding: Heavy, expensive hardware (LiDAR, physical sonar) is being successfully replaced by advanced software-based depth estimation.",
        "Specific Methodological Evidence:",
        "  - Das et al. (2025) [Paper 13]: Validated that integrated monocular depth estimation on-device reduces Mean Absolute Error (MAE) and supports reliable distance measurement.",
        "  - Li et al. (2025) [Paper 19]: Showed that reducing hardware bulk mitigates the social stigma associated with heavy wearable AI.",
        "Our Framework Application: Our system integrates depth estimation software to provide spatial awareness directly from minimum smartphone camera inputs."
    ])

    # Slide 5
    add_slide(prs, 1, "Trend 3: Multimodal & Cross-Modal Interfaces", [
        "Finding: Purely audio-based systems increase cognitive load. The leading solutions now employ haptic/vibration cross-modal feedback.",
        "Specific Methodological Evidence:",
        "  - Spiers et al. (2024) [Paper 11]: Achieved 'parity with sighted vision' in navigation accuracy using shape-changing haptics over audio-only.",
        "  - Narayanan et al. (2024) [Paper 14]: Demonstrated multimodal feedback significantly reduced object-retrieval times.",
        "  - Fei et al. (2024) [Paper 22]: Confirmed that vibration matrices successfully convey critical directional data.",
        "Our Framework Application: Incorporating selective vibration zones alongside audio to reduce 'Alert Fatigue'."
    ])

    # Slide 6
    add_slide(prs, 1, "Research Gap 1: High Latency & Cloud Dependency", [
        "Identified Gap: The reliance on cloud-API models introduces extreme safety risks during navigation.",
        "Specific Evidence from RRL:",
        "  - Zhang et al. (2024) [Paper 17]: Showed that while NaviGPT (using GPT-4 Vision) provided great descriptions, users suffered from 2 to 5-second network delays, rendering it unsafe for walking.",
        "  - Dabbrata Das et al. (2025) [Paper 28]: Proven that a fully offline PathFinder system allowed 80% of blind users to operate safely without internet dependency.",
        "Our Solution Design: 100% Offline capability ensures split-second hazard alerts regardless of network environment."
    ])

    # Slide 7
    add_slide(prs, 1, "Research Gap 2: Hazard Priority and 'Thin Objects'", [
        "Identified Gap: Blanket obstacle detection overwhelms users, and models often fail on narrow, critical dangers (e.g., chains, poles).",
        "Specific Evidence from RRL:",
        "  - Li et al. (2025) [Paper 18]: Developed PC-CS-YOLO specifically because standard detection misses 'thin' hazards, causing dangerous collisions.",
        "  - Li, Z. et al. (2025) [Paper 19]: Highlighted the necessity of implementing an 'intelligent interaction module' to rank and identify the 'core obstacle' over harmless background objects.",
        "Our Solution Design: Development of a Priority Engine to rank identified hazards in real-time by depth and risk factor."
    ])

    # Slide 8
    add_slide(prs, 1, "System Architecture: Bridging the Gaps", [
        "Based on our synthesis of 30 papers, our system is architected as:",
        "1. Visual Model: YOLOv8 trained specifically on indoor/outdoor navigation hazards (avoiding generic datasets like COCO).",
        "2. Spatial Model: TFLite-based Monocular Depth Estimation to replace bulky hardware.",
        "3. Cognitive Workflow:",
        "    - Raw Detection -> Depth Correlation -> Priority Ranking -> Multimodal Alert (Vibrate + Audio).",
        "4. Deployment Constraint:",
        "    - Strictly offline inference protecting privacy and ensuring <300ms total latency."
    ])

    # Slide 9
    add_slide(prs, 1, "Conclusion: Readiness for Development", [
        "The evaluation of 30 specialized global studies comprehensively validates our direction:",
        "  - Object Detection alone is no longer scientifically novel; the focus is now on Speed, Offline capability, and Cognitive Feedback.",
        "By focusing on:",
        "  1. Edge inference to eliminate cloud lag.",
        "  2. Multimodal alerts to reduce anxiety.",
        "  3. Risk-aware priority sorting...",
        "We address the primary barriers identified in international trials (2021-2026).",
        "",
        "Thank You. The floor is open for questions."
    ])

    # Save presentation
    output_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(output_path)
    print(f"Presentation successfully saved to: {output_path}")

if __name__ == "__main__":
    parser = ArgumentParser(description="Generate the Group 8 RRL presentation.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "docs" / "03_Presentation" / "Group8_Defense_Presentation.pptx",
    )
    parser.add_argument("--force", action="store_true", help="Replace an existing presentation.")
    args = parser.parse_args()
    output_path = args.output.resolve()
    if output_path.exists() and not args.force:
        parser.error(f"Output already exists: {output_path}. Pass --force to replace it.")
    generate_presentation(output_path)
