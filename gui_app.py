import PySimpleGUI as sg
from PIL import Image
import os
import zipfile


# === Fonction de watermark ===
def apply_watermark(image_path, watermark_path, position, scale):
    image = Image.open(image_path).convert("RGBA")
    watermark = Image.open(watermark_path).convert("RGBA")

    # Redimensionnement dynamique du filigrane
    w_ratio = scale * image.width / watermark.width
    new_size = (int(watermark.width * w_ratio), int(watermark.height * w_ratio))
    watermark = watermark.resize(new_size, Image.LANCZOS)

    # Positionnement
    if position == "En bas à droite":
        x = image.width - watermark.width - 10
        y = image.height - watermark.height - 10
    elif position == "En bas au centre":
        x = (image.width - watermark.width) // 2
        y = image.height - watermark.height - 10
    elif position == "En bas à gauche":
        x = 10
        y = image.height - watermark.height - 10
    elif position == "En haut à droite":
        x = image.width - watermark.width - 10
        y = 10
    elif position == "En haut à gauche":
        x = 10
        y = 10
    elif position == "Centre":
        x = (image.width - watermark.width) // 2
        y = (image.height - watermark.height) // 2
    else:
        x, y = 0, 0

    image.paste(watermark, (x, y), watermark)
    return image.convert("RGB")


# === Traitement des images ===
def process_images(input_folder, watermark_path, position, scale, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    supported_formats = (".jpg", ".jpeg", ".png")

    for file in os.listdir(input_folder):
        if file.lower().endswith(supported_formats):
            input_path = os.path.join(input_folder, file)
            output_path = os.path.join(output_folder, file)
            try:
                watermarked = apply_watermark(
                    input_path, watermark_path, position, scale
                )
                watermarked.save(output_path)
            except Exception as e:
                print(f"Erreur sur {file} : {e}")


# === Création du fichier ZIP ===
def zip_output(output_folder, zip_path):
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for root, _, files in os.walk(output_folder):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, output_folder)
                zipf.write(full_path, arcname)


# === Interface graphique ===
sg.theme("LightBlue")

layout = [
    [sg.Text("Dossier d’images"), sg.InputText(key="FOLDER"), sg.FolderBrowse()],
    [
        sg.Text("Filigrane (PNG, JPG, etc.)"),
        sg.InputText(key="WATERMARK"),
        sg.FileBrowse(file_types=(("Image Files", "*.png;*.jpg;*.jpeg"),)),
    ],
    [
        sg.Text("Position du filigrane"),
        sg.Combo(
            [
                "En bas à droite",
                "En bas au centre",
                "En bas à gauche",
                "En haut à droite",
                "En haut à gauche",
                "Centre",
            ],
            default_value="En bas à droite",
            key="POSITION",
        ),
    ],
    [
        sg.Text("Taille du filigrane (%)"),
        sg.Slider(
            range=(5, 50), default_value=25, orientation="h", resolution=1, key="SCALE"
        ),
    ],
    [sg.Button("Lancer le traitement"), sg.Button("Créer ZIP"), sg.Button("Quitter")],
    [sg.Text("", size=(50, 2), key="STATUS")],
]

window = sg.Window("Retouche Photo - Filigrane", layout)

output_folder = "output"
zip_path = "output.zip"

while True:
    event, values = window.read()
    if event in (sg.WINDOW_CLOSED, "Quitter"):
        break
    elif event == "Lancer le traitement":
        folder = values["FOLDER"]
        watermark = values["WATERMARK"]
        position = values["POSITION"]
        scale_percent = values["SCALE"]

        if not folder or not watermark:
            window["STATUS"].update("Veuillez sélectionner un dossier et un filigrane.")
            continue

        scale_ratio = float(scale_percent) / 100.0  # Conversion en [0.05 - 0.5]
        process_images(folder, watermark, position, scale_ratio, output_folder)
        window["STATUS"].update(
            f"✅ Images enregistrées dans le dossier '{output_folder}/'"
        )
    elif event == "Créer ZIP":
        if not os.path.exists(output_folder):
            window["STATUS"].update("❌ Aucune image trouvée à zipper.")
            continue
        zip_output(output_folder, zip_path)
        window["STATUS"].update(f"✅ Archive ZIP créée : {zip_path}")

window.close()
