from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from rembg import remove
from PIL import Image
import io, os

app = Flask(__name__)

# CORS'u sadece Netlify frontend için aç
CORS(app, resources={r"/*": {"origins": "https://astonishing-tulumba-97ae61.netlify.app"}})

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Backend çalışıyor 🚀"})

@app.route("/arka-plan-kaldir", methods=["POST"])
def arka_plan_kaldir():
    if "file" not in request.files:
        return jsonify({"error": "Dosya yüklenmedi"}), 400

    file = request.files["file"]

    try:
        input_image = Image.open(file.stream)
        output_image = remove(input_image)

        img_io = io.BytesIO()
        output_image.save(img_io, format="PNG")
        img_io.seek(0)

        return send_file(img_io, mimetype="image/png")

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
