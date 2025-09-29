from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import io
from rembg import remove
from PIL import Image

app = Flask(__name__)
CORS(app)

# Sağlık kontrolü için kök endpoint
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "message": "Backend çalışıyor 🚀"}), 200

# Arka plan kaldırma endpoint
@app.route("/arka-plan-kaldir", methods=["POST"])
def arka_plan_kaldir():
    if "file" not in request.files:
        return jsonify({"error": "Dosya yüklenmedi"}), 400

    file = request.files["file"]
    input_image = Image.open(file.stream).convert("RGBA")
    output_image = remove(input_image)

    img_io = io.BytesIO()
    output_image.save(img_io, "PNG")
    img_io.seek(0)
    return send_file(img_io, mimetype="image/png")

if __name__ == "__main__":
    # Render için PORT environment variable kullan
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
