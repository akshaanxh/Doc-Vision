# SmartDoc Vision
## A Computer Vision Based Document Scanner for Student Notes and Assignment Sheets

---

## Abstract

This project presents **SmartDoc Vision**, a lightweight computer vision system that converts casual photographs of documents into clean scan-like images. In everyday student life, notes, assignments, lab records, and printed sheets are frequently captured using mobile cameras. These images usually suffer from perspective distortion, skew, shadows, and low readability. The project solves this problem using classical computer vision techniques such as edge detection, thresholding, contour analysis, perspective transformation, and image enhancement. The final system accepts one or more images, detects the document boundary, rectifies the page to a top-down view, improves readability, and can optionally combine multiple outputs into a PDF. The project demonstrates how core computer vision concepts can be combined into a practical and meaningful real-world solution.

---

## 1. Introduction

Computer Vision is not only about complex deep learning models. Many useful real-world problems can be solved effectively using classical image processing and geometry. One such problem is **document scanning from mobile camera images**.

Students often photograph notes instead of scanning them using dedicated devices. However, these photos are rarely ideal. The page may be tilted, partially rotated, captured from an angle, or affected by bad lighting conditions. Such images are uncomfortable to read, difficult to archive, and sometimes unsuitable for online submission.

This project aims to build a simple but practical system that automatically transforms a raw photo of a page into a much cleaner digital document.

---

## 2. Problem Statement

The chosen problem is:

**How can a mobile photo of a notebook page or printed document be automatically converted into a clean, readable, scan-like result using computer vision techniques?**

The main challenges are:

- document boundaries are not perfectly aligned with the image frame
- the page may be captured from an oblique angle
- there may be background clutter around the document
- lighting conditions may not be uniform
- the final output should look closer to a flat scanned page

---

## 3. Motivation

This problem is directly relevant to student life and academic workflows. In my environment, students often:

- click photos of classroom notes
- submit photographed assignment sheets
- share handwritten study material through messaging apps
- store printed notices or forms as images

A document scanner solves a real and repeated problem. It is also a very suitable Computer Vision BYOP because it naturally uses multiple foundational course concepts in one pipeline.

---

## 4. Objectives

The main objectives of the project are:

1. Detect the document region automatically from an image.
2. Correct perspective distortion and obtain a top-down document view.
3. Improve readability through thresholding and enhancement.
4. Support both single-image and multi-image workflows.
5. Provide optional PDF export for scanned pages.
6. Keep the solution lightweight, explainable, and easy to run.

---

## 5. Why this project is suitable for the course

This project strongly matches the Computer Vision course because it uses:

- image representation and preprocessing
- smoothing and noise reduction
- edge detection
- contour detection and shape approximation
- geometric transformation
- thresholding and morphology
- practical system integration

Rather than using only one isolated concept, the project builds an end-to-end vision system.

---

## 6. Scope of the Project

### Included in scope

- document detection from a normal photo
- perspective correction
- scan-like enhancement
- batch processing for multiple images
- PDF generation from output scans
- optional browser UI using Streamlit

### Out of scope

- OCR-based text recognition
- semantic understanding of document content
- real-time mobile deployment
- deep learning based page detection
- advanced shadow removal and dewarping for curved pages

---

## 7. System Design

The pipeline is designed as a sequence of classical computer vision operations.

### 7.1 High-level flow

Input image -> resize -> grayscale -> blur -> edge/threshold analysis -> contour detection -> quadrilateral selection -> perspective transform -> enhancement -> output image/PDF

### 7.2 Design rationale

The project deliberately uses classical CV instead of a heavy neural network because:

- the problem is structured and geometric
- the system needs to be lightweight
- the pipeline should be explainable in a course setting
- the code should be runnable on a normal laptop without GPU support

---

## 8. Methodology

### 8.1 Input acquisition

The project accepts either:

- a single image path, or
- a folder of images

Supported image formats include `.jpg`, `.jpeg`, `.png`, `.bmp`, and `.webp`.

### 8.2 Image resizing

Large images increase computational cost. Therefore, each image is resized to a fixed height while preserving aspect ratio. This speeds up processing and keeps contour detection stable.

### 8.3 Grayscale conversion and Gaussian blur

Color information is not necessary for document boundary detection. The image is converted to grayscale and then blurred using a Gaussian kernel. This reduces noise and small texture details that might otherwise create false edges.

### 8.4 Edge-based document evidence

The blurred grayscale image is passed through the **Canny edge detector**. This step highlights strong intensity transitions, which often correspond to page boundaries.

### 8.5 Bright-region document evidence

In parallel, **Otsu thresholding** is applied to isolate the brighter paper region from the darker background. This improves robustness when edge maps alone are not sufficient.

### 8.6 Contour detection

Contours are extracted from both the edge map and the threshold mask. Candidate contours are sorted by area. The system searches for a contour that:

- has four vertices after polygon approximation
- occupies a meaningful area of the image
- is likely to represent the document page

### 8.7 Polygon approximation

For each contour, the perimeter is computed and the contour is simplified using polygon approximation. A good document contour should ideally reduce to a quadrilateral.

### 8.8 Perspective correction

Once the four page corners are detected, they are ordered consistently as:

- top-left
- top-right
- bottom-right
- bottom-left

These points are then mapped to a rectangular coordinate system using a perspective transform. This creates a top-down view similar to a scanner output.

### 8.9 Image enhancement

The warped document is enhanced using the following steps:

- grayscale conversion
- mild smoothing
- CLAHE for local contrast improvement
- adaptive thresholding for scan-like black/white output
- morphological closing to remove tiny holes and speckles

### 8.10 PDF generation

If multiple pages are scanned, the outputs can be combined into a PDF using the Pillow library.

---

## 9. Algorithmic Explanation

### 9.1 Canny edge detection

Canny identifies strong gradients in the image. It is useful because document boundaries usually form clear contrast transitions relative to the background.

### 9.2 Contours and shape analysis

Contours provide a way to convert an edge map or threshold mask into geometric candidate regions. By ranking contours by area and checking for four-corner approximations, the system can recover a page-shaped object.

### 9.3 Perspective transformation

A photo taken from an angle introduces projective distortion. The perspective transform maps the four detected corners of the page into a rectangle, effectively flattening the image.

### 9.4 Adaptive thresholding

Global thresholding fails when illumination varies across the page. Adaptive thresholding computes thresholds locally, which helps preserve readability under uneven lighting.

### 9.5 Morphological operations

Morphological closing fills tiny gaps and smooths the binary result. This improves the visual quality of the final scanned page.

---

## 10. Implementation Details

### Programming language
- Python

### Libraries used
- OpenCV
- NumPy
- Pillow
- Streamlit

### Main files

- `app.py` - command-line entry point
- `streamlit_app.py` - optional browser interface
- `src/document_scanner.py` - main scanning logic
- `src/pdf_utils.py` - PDF export helper
- `scripts/generate_sample_inputs.py` - synthetic demo image generator

---

## 11. Project Structure

```text
byop_cv_project/
├── app.py
├── streamlit_app.py
├── requirements.txt
├── README.md
├── src/
│   ├── document_scanner.py
│   └── pdf_utils.py
├── scripts/
│   └── generate_sample_inputs.py
├── assets/
│   ├── sample_inputs/
│   └── sample_outputs/
└── report/
    ├── project_report.md
    └── project_report.docx
```

---

## 12. Experimental Demonstration

The project was tested on synthetic sample images representing photographed notes and assignment-style pages. The system successfully:

- detected the page contour
- corrected the page orientation and perspective
- generated clean binary scan-like images
- exported multiple scanned pages into a single PDF

The debug option also saved intermediate images such as:

- resized input
- edge map
- detected contour visualization
- warped color output
- final scanned binary image

These intermediate results are useful for both debugging and report presentation.

---

## 13. Observations

The system performs best when:

- the page boundary is visible
- the page occupies a large portion of the image
- the paper contrasts well with the background
- blur is moderate rather than extreme

The dual strategy of combining edge-based and threshold-based evidence improved robustness over using only one of them.

---

## 14. Challenges Faced

During project design, the following practical challenges appeared:

### 14.1 False contour selection
Sometimes edge maps produce many irrelevant contours from text, shadows, or background patterns. This was reduced by sorting contours by area and enforcing a minimum page-area condition.

### 14.2 Dependence on lighting
A single global threshold is often not enough for uneven illumination. Adaptive thresholding and CLAHE improved the visual quality of the final scan.

### 14.3 Warping artifacts near borders
Perspective correction can introduce small border artifacts. A tiny crop margin after enhancement helped remove these visual defects.

### 14.4 Need for a realistic but lightweight system
A deep learning detector could make the system more robust, but it would add unnecessary complexity for a course project. The final design balances practicality and simplicity.

---

## 15. Limitations

The current version has some limitations:

- it assumes the document is approximately rectangular
- extreme blur or occlusion may break detection
- strong shadows are not fully removed
- curved pages are not flattened
- very cluttered scenes can still confuse the contour ranking step

---

## 16. Future Work

This project can be extended in several directions:

1. Add manual corner adjustment when auto-detection fails.
2. Integrate OCR for searchable text output.
3. Build a mobile app using the same scanning pipeline.
4. Add real-time webcam scanning.
5. Use a deep learning document detector for complex backgrounds.
6. Add shadow suppression and page dewarping for notebook images.
7. Export searchable PDF by combining OCR with the scanned image.

---

## 17. Real-World Impact

Even though the project is technically simple compared to large AI systems, it solves a useful real-world problem directly relevant to students and office users. It demonstrates that a meaningful solution can emerge from thoughtful application of foundational computer vision methods.

The project is also a good example of engineering judgment: choosing a solution that is explainable, efficient, and appropriate to the problem instead of overcomplicating it.

---

## 18. Learning Outcomes

Through this project, I learned:

- how multiple image processing steps interact in a full pipeline
- how geometric reasoning is used in practical vision systems
- how contour analysis can be used for object localization
- how perspective correction works in a real application
- how enhancement techniques affect readability and user experience
- how to convert a course concept into a usable software tool

This project also strengthened my understanding of how to design a system around user needs rather than only around algorithms.

---

## 19. Conclusion

SmartDoc Vision is a practical BYOP project that solves a familiar real-world problem using core computer vision techniques. The system detects a document in an image, corrects its perspective, enhances readability, and supports PDF export. The project is purposeful, technically relevant to the course, and demonstrates clear understanding of both theory and implementation.

It shows that classical computer vision is still highly valuable for many structured problems and can deliver elegant solutions without heavy computation.

---

## 20. References

1. Richard Szeliski, *Computer Vision: Algorithms and Applications*.
2. Rafael C. Gonzalez and Richard E. Woods, *Digital Image Processing*.
3. OpenCV Documentation - image processing, contour detection, geometric transformations.
4. Course concepts from the Computer Vision syllabus and lab practice.
