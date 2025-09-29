from flask import Flask, request, send_file
from flask_cors import CORS
import rembg
from PIL import Image
import io
import os

app = Flask(__name__)
CORS(app)  # Frontend (Netlify) ile iletişim için gerekli

# Ana endpoint
@app.route("/")
def home():
    return {"status": "Backend çalışıyor 🚀"}

# Arka plan kaldırma endpoint
@app.route("/arka-plan-kaldir", methods=["POST"])
def arka_plan_kaldir():
    if "file" not in request.files:
        return {"error": "Dosya bulunamadı"}, 400

    file = request.files["file"]
    input_image = file.read()

    # Rembg ile arka plan kaldır
    output_image = rembg.remove(input_image)

    return send_file(
        io.BytesIO(output_image),
        mimetype="image/png",
        as_attachment=False,
        download_name="sonuc.png"
    )

# Render uyumlu çalıştırma
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render PORT değişkenini alır
    app.run(host="0.0.0.0", port=port)
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render portunu kullanır
    app.run(host="0.0.0.0", port=port)
