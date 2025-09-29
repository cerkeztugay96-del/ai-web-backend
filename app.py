from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from rembg import remove
from PIL import Image
import io
import os

app = Flask(__name__)
# Netlify gibi dış sitelerden gelen istekler için CORS tamamen açık
CORS(app, resources={r"/*": {"origins": "*"}})


# Backend çalışıyor mu test için
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Backend calisiyor"})


# Arka plan kaldırma endpointi
@app.route("/arka-plan-kaldir", methods=["POST"])
def arka_plan_kaldir():
    if "file" not in request.files:
        return jsonify({"error": "Dosya yuklenmedi"}), 400

    file = request.files["file"]

    try:
        # Yüklenen dosyayı oku
        input_image = Image.open(file.stream)

        # Arka planı kaldır
        output_image = remove(input_image)

        # Çıktıyı byte stream’e PNG olarak kaydet
        img_io = io.BytesIO()
        output_image.save(img_io, format="PNG")
        img_io.seek(0)

        # PNG sonucu döndür
        return send_file(img_io, mimetype="image/png")

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
