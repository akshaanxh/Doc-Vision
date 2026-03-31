from __future__ import annotations

from io import BytesIO

import cv2
import numpy as np
import streamlit as st
from PIL import Image

from src.document_scanner import DocumentScanner

st.set_page_config(page_title="SmartDoc Vision", layout="wide")
st.title("SmartDoc Vision - Document Scanner")
st.write(
    "Upload a photo of a notebook page, assignment sheet, or printed document. "
    "The app will detect the page boundary, correct perspective, and generate a scan-like result."
)

uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png", "webp", "bmp"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    image_np = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    scanner = DocumentScanner()
    result = scanner.scan(image_np)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Original")
        st.image(image, use_container_width=True)

    with col2:
        st.subheader("Scanned Output")
        if result.success:
            st.image(result.scanned, clamp=True, use_container_width=True)

            pil_scan = Image.fromarray(result.scanned)
            buffer = BytesIO()
            pil_scan.save(buffer, format="PNG")
            st.download_button(
                "Download scanned image",
                data=buffer.getvalue(),
                file_name="scanned_output.png",
                mime="image/png",
            )
        else:
            st.error(result.message)

    with st.expander("Show processing steps"):
        debug_images = scanner.debug_images(result)
        for name, debug_image in debug_images.items():
            st.markdown(f"**{name}**")
            st.image(debug_image, clamp=True, use_container_width=True)
else:
    st.info("Upload an image to start.")
