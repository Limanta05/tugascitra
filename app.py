import gradio as gr
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import io
import matplotlib.pyplot as plt
import numpy as np

def apply_filters(image, brightness=0, contrast=0, filter_type="None", filter_intensity=5, rotation=0):
    if image is None:
        return None, None, "Belum ada gambar yang diproses."

    img = image.convert("RGB")
    img = ImageEnhance.Brightness(img).enhance(1 + brightness / 100)
    img = ImageEnhance.Contrast(img).enhance(1 + contrast / 100)

    if filter_type == "Grayscale":
        img = ImageOps.grayscale(img).convert("RGB")
    elif filter_type == "Sepia":
        sepia_img = np.array(img)
        r, g, b = sepia_img[..., 0], sepia_img[..., 1], sepia_img[..., 2]
        tr = np.clip((0.393 + 0.05 * (filter_intensity - 5)) * r +
                     (0.769 + 0.05 * (filter_intensity - 5)) * g +
                     (0.189 + 0.05 * (filter_intensity - 5)) * b, 0, 255)
        tg = np.clip((0.349 + 0.05 * (filter_intensity - 5)) * r +
                     (0.686 + 0.05 * (filter_intensity - 5)) * g +
                     (0.168 + 0.05 * (filter_intensity - 5)) * b, 0, 255)
        tb = np.clip((0.272 + 0.05 * (filter_intensity - 5)) * r +
                     (0.534 + 0.05 * (filter_intensity - 5)) * g +
                     (0.131 + 0.05 * (filter_intensity - 5)) * b, 0, 255)
        sepia = np.stack([tr, tg, tb], axis=-1).astype(np.uint8)
        img = Image.fromarray(sepia)
    elif filter_type == "Negative":
        img = ImageOps.invert(img)
    elif filter_type == "Blur":
        img = img.filter(ImageFilter.GaussianBlur(radius=filter_intensity))
    elif filter_type == "Sharpen":
        img = ImageEnhance.Sharpness(img).enhance(filter_intensity)

    img = img.rotate(rotation, expand=True)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    file_size_kb = round(len(buffer.getvalue()) / 1024, 2)
    edited_size = img.size
    edited_mode = img.mode
    dpi_info = image.info.get("dpi", (0, 0))
    dpi_text = f"{dpi_info[0]} x {dpi_info[1]} DPI" if dpi_info != (0, 0) else "Tidak diketahui"

    metadata = (
        f"📐 Ukuran Setelah Edit: {edited_size[0]} x {edited_size[1]} px\n"
        f"🎨 Mode Warna: {edited_mode}\n"
        f"📂 Format: PNG\n"
        f"💾 Ukuran File: {file_size_kb} KB\n"
        f"🧭 Resolusi (DPI): {dpi_text}"
    )

    gray = img.convert("L")
    hist = gray.histogram()
    fig, ax = plt.subplots(figsize=(4, 2))
    ax.plot(hist, color='black')
    ax.set_title("Histogram")
    ax.set_xlabel("Pixel Intensity")
    ax.set_ylabel("Jumlah")
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    hist_image = Image.open(buf)

    return img, hist_image, metadata

def show_guide():
    return """📘 Panduan Penggunaan Aplikasi

1. Unggah gambar menggunakan panel Unggah Gambar.
2. Sesuaikan:
   - 🌞 Kecerahan
   - 🎚️ Kontras
   - 🎨 Filter dan Intensitas
   - 🔄 Rotasi
3. Gambar, informasi, dan histogram akan diperbarui otomatis.
4. Klik tombol 📘 untuk menampilkan panduan ini lagi.

🎉 Selamat mengedit gambar!"""

with gr.Blocks(theme=gr.themes.Soft(primary_hue="violet")) as demo:
    gr.Markdown("## 🎨 Peningkatan Kualitas Gambar by Kelompok 8")

    with gr.Row(equal_height=True):
        with gr.Column(scale=1):
            image_input = gr.Image(type="pil", label="📥 Unggah Gambar")
            brightness = gr.Slider(-100, 100, step=1, value=20, label="🌞 Kecerahan")
            contrast = gr.Slider(-100, 100, step=1, value=0, label="🎚️ Kontras")
            filter_type = gr.Radio(["None", "Grayscale", "Sepia", "Negative", "Blur", "Sharpen"],
                                   label="🎨 Filter", value="None")
            filter_intensity = gr.Slider(0, 10, step=1, value=5, label="⚙️ Intensitas Filter")
            rotation = gr.Slider(-180, 180, step=1, value=0, label="🔄 Rotasi")

        with gr.Column(scale=1):
            output_img = gr.Image(type="pil", label="🖼️ Hasil Edit")
            metadata = gr.Textbox(label="📝 Informasi Gambar", lines=6)
            histogram = gr.Image(type="pil", label="📊 Histogram")
            guide_button = gr.Button("📘 Tampilkan Panduan")
            guide_text = gr.Textbox(label="📖 Panduan", visible=False, lines=6)

    inputs = [image_input, brightness, contrast, filter_type, filter_intensity, rotation]
    outputs = [output_img, histogram, metadata]

    for comp in inputs:
        comp.change(fn=apply_filters, inputs=inputs, outputs=outputs, show_progress=False)

    guide_button.click(fn=show_guide, inputs=[], outputs=guide_text, show_progress=False)
    guide_button.click(lambda: gr.update(visible=True), None, guide_text, show_progress=False)

if __name__ == '__main__':
    demo.launch()
