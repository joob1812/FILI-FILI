import os
import zipfile
import shutil
import uuid
from flask import Flask, render_template, request, send_file
from PIL import Image

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

POSITIONS = {
    "bottom_right": lambda img, wm: (
        img.width - wm.width - 10,
        img.height - wm.height - 10,
    ),
    "bottom_center": lambda img, wm: (
        (img.width - wm.width) // 2,
        img.height - wm.height - 10,
    ),
    "bottom_left": lambda img, wm: (10, img.height - wm.height - 10),
    "top_right": lambda img, wm: (img.width - wm.width - 10, 10),
    "top_left": lambda img, wm: (10, 10),
    "center": lambda img, wm: (
        (img.width - wm.width) // 2,
        (img.height - wm.height) // 2,
    ),
}


def apply_watermark(image_path, watermark_path, position, scale):
    image = Image.open(image_path).convert("RGBA")
    watermark = Image.open(watermark_path).convert("RGBA")

    ratio = (scale / 100.0) * image.width / watermark.width
    new_size = (int(watermark.width * ratio), int(watermark.height * ratio))
    watermark = watermark.resize(new_size, Image.LANCZOS)

    x, y = POSITIONS.get(position, POSITIONS["bottom_right"])(image, watermark)
    image.paste(watermark, (x, y), watermark)
    return image.convert("RGB")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        files = request.files.getlist("photos")
        watermark = request.files.get("watermark")
        position = request.form.get("position")
        scale = int(request.form.get("scale", 25))

        if not files or not watermark:
            return "❌ Veuillez fournir des images et un filigrane.", 400

        session_id = str(uuid.uuid4())
        session_folder = os.path.join(PROCESSED_FOLDER, session_id)
        os.makedirs(session_folder, exist_ok=True)

        watermark_path = os.path.join(UPLOAD_FOLDER, f"{session_id}_watermark.png")
        watermark.save(watermark_path)

        for f in files:
            filename = f.filename
            image_path = os.path.join(UPLOAD_FOLDER, f"{session_id}_{filename}")
            f.save(image_path)

            try:
                output_image = apply_watermark(
                    image_path, watermark_path, position, scale
                )
                output_path = os.path.join(session_folder, filename)
                output_image.save(output_path)
            except Exception as e:
                print(f"Erreur sur {filename} : {e}")

        zip_filename = f"{session_id}.zip"
        zip_path = os.path.join(PROCESSED_FOLDER, zip_filename)
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for file in os.listdir(session_folder):
                zipf.write(os.path.join(session_folder, file), file)

        shutil.rmtree(session_folder)
        os.remove(watermark_path)
        for f in files:
            os.remove(os.path.join(UPLOAD_FOLDER, f"{session_id}_{f.filename}"))

        return send_file(zip_path, as_attachment=True)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
