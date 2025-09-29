from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from rembg import remove
from PIL import Image
import io
import os

app = Flask(__name__)
CORS(app)  # CORS açık, Netlify erişebilir


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Backend calisiyor"})


@app.route("/arka-plan-kaldir", methods=["POST"])
def arka_plan_kaldir():
    if "file" not in request.files:
        return jsonify({"error": "Dosya yuklenmedi"}), 400

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
