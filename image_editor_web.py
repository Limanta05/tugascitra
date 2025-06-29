# image_editor_web.py (versi Streamlit)
import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter
import matplotlib.pyplot as plt
import numpy as np
import cv2
import io
import base64
from datetime import datetime

st.set_page_config(layout="wide")
st.title("Web Image Editor")

# Session State Initialization
if 'original_image' not in st.session_state:
    st.session_state.original_image = None
    st.session_state.current_image = None
    st.session_state.display_image = None
    st.session_state.brightness = 0
    st.session_state.contrast = 0
    st.session_state.rotation = 0
    st.session_state.zoom = 1.0
    st.session_state.filter = None
    st.session_state.filter_intensity = 5

def apply_filters(img):
    img = img.copy()
    intensity = st.session_state.filter_intensity
    if st.session_state.filter == "Grayscale":
        img = img.convert("L").convert("RGB")
    elif st.session_state.filter == "Sepia":
        img = apply_sepia(img, intensity)
    elif st.session_state.filter == "Negative":
        img = Image.eval(img, lambda x: 255 - int((x * intensity / 10)))
    elif st.session_state.filter == "Blur":
        img = img.filter(ImageFilter.GaussianBlur(radius=intensity))
    elif st.session_state.filter == "Sharpen":
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(intensity)
    return img

def apply_sepia(img, intensity=5):
    img = img.convert("RGB")
    pixels = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pixels[x, y]
            tr = int((0.393 + 0.05 * (intensity - 5)) * r + (0.769 + 0.05 * (intensity - 5)) * g + (0.189 + 0.05 * (intensity - 5)) * b)
            tg = int((0.349 + 0.05 * (intensity - 5)) * r + (0.686 + 0.05 * (intensity - 5)) * g + (0.168 + 0.05 * (intensity - 5)) * b)
            tb = int((0.272 + 0.05 * (intensity - 5)) * r + (0.534 + 0.05 * (intensity - 5)) * g + (0.131 + 0.05 * (intensity - 5)) * b)
            pixels[x, y] = (min(255, tr), min(255, tg), min(255, tb))
    return img

def apply_adjustments(img):
    img = ImageEnhance.Brightness(img).enhance(1 + st.session_state.brightness / 100)
    img = ImageEnhance.Contrast(img).enhance(1 + st.session_state.contrast / 100)
    img = img.rotate(st.session_state.rotation, expand=True)
    if st.session_state.zoom != 1.0:
        new_size = (int(img.width * st.session_state.zoom), int(img.height * st.session_state.zoom))
        img = img.resize(new_size)
    return img

def update_image():
    img = st.session_state.original_image.copy()
    img = apply_adjustments(img)
    img = apply_filters(img)
    st.session_state.current_image = img

def plot_histogram(img):
    fig, ax = plt.subplots()
    gray = img.convert('L')
    hist = gray.histogram()
    ax.plot(hist, color='black')
    ax.set_title('Histogram')
    ax.set_xlabel('Intensity')
    ax.set_ylabel('Frequency')
    st.pyplot(fig)

# Sidebar
with st.sidebar:
    st.header("Input Gambar")
    uploaded_file = st.file_uploader("Unggah Gambar", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        st.session_state.original_image = image
        update_image()

    if st.session_state.original_image:
        st.divider()
        st.header("Penyesuaian")
        st.session_state.brightness = st.slider("Brightness", -100, 100, st.session_state.brightness)
        st.session_state.contrast = st.slider("Contrast", -100, 100, st.session_state.contrast)
        st.session_state.rotation = st.slider("Rotasi", -180, 180, st.session_state.rotation)
        st.session_state.zoom = st.slider("Zoom", 0.2, 3.0, st.session_state.zoom)

        st.divider()
        st.header("Filter")
        st.session_state.filter = st.selectbox("Pilih Filter", [None, "Grayscale", "Sepia", "Negative", "Blur", "Sharpen"])
        st.session_state.filter_intensity = st.slider("Intensitas Filter", 0, 10, st.session_state.filter_intensity)

        if st.button("Terapkan Perubahan"):
            update_image()

# Main Panel
if st.session_state.current_image:
    col1, col2 = st.columns(2)
    with col1:
        st.image(st.session_state.original_image, caption="Original", use_column_width=True)
    with col2:
        st.image(st.session_state.current_image, caption="Hasil Edit", use_column_width=True)
        st.download_button("Download Gambar", data=io.BytesIO(np.array(st.session_state.current_image)).getvalue(),
                           file_name="edited_image.png")
        st.subheader("Histogram")
        plot_histogram(st.session_state.current_image)
else:
    st.info("Unggah gambar terlebih dahulu untuk mulai mengedit.")
