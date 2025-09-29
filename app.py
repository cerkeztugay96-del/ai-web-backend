from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from rembg import remove, new_session
from PIL import Image
import io, os

app = Flask(__name__)

# Netlify siteden gelen isteklere izin ver
CORS(app, resources={r"/*": {"origins": "https://astonishing-tulumba-97ae61.netlify.app"}})

# Model klasörü (runtime'da tekrar indirmesin)
os.environ.setdefault("U2NET_HOME", "/opt/render/.u2net")
os.makedirs(os.environ["U2NET_HOME"], exist_ok=True)

# HAFİF MODELİ ÖNDEN YÜKLE (4.7 MB)
# Büyük: "u2net" (176MB)  -> yavaş + OOM riski
# Küçük: "u2netp" (4.7MB) -> hızlı + düşük RAM
session = new_session("u2netp")


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Backend calisiyor 🚀"})


@app.route("/arka-plan-kaldir", methods=["POST"])
def arka_plan_kaldir():
    if "file" not in request.files:
        return jsonify({"error": "Dosya yuklenmedi"}), 400

    file = request.files["file"]
    try:
        input_image = Image.open(file.stream).convert("RGBA")
        # Önden yüklediğimiz session ile çalış
        output_image = remove(input_image, session=session)

        img_io = io.BytesIO()
        output_image.save(img_io, format="PNG")
        img_io.seek(0)
        return send_file(img_io, mimetype="image/png")

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
