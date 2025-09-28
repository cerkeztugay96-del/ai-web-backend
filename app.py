from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from rembg import remove, new_session
from PIL import Image
import io, os

app = Flask(__name__)
# Maks. 20 MB yükleme
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024

# Sadece kendi sitene izin ver + local geliştirme
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://ilterayreklam.netlify.app",
            "http://localhost:5173",
            "http://127.0.0.1:5173"
        ]
    }
})

# IS-Net oturumu (U²-Net iyileştirilmiş sürüm)
session = new_session("isnet-general-use")

@app.route("/")
def home():
    return "Backend IS-Net ile çalışıyor! 🎉"

@app.route("/healthz")
def healthz():
    return jsonify({"ok": True})

@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "Dosya çok büyük (20MB sınır)."}), 413

@app.route("/remove-bg", methods=["POST"])
def remove_bg():
    if "file" not in request.files:
        return jsonify({"error": "Dosya yüklenmedi"}), 400

    f = request.files["file"]
    try:
        img = Image.open(f.stream).convert("RGBA")
    except Exception:
        return jsonify({"error": "Geçersiz görüntü dosyası"}), 400

    # Arka planı kaldır
    out = remove(img, session=session)

    buf = io.BytesIO()
    out.save(buf, "PNG", optimize=True)
    buf.seek(0)

    # İndirilebilir dosya gibi de davranır
    return send_file(
        buf,
        mimetype="image/png",
        as_attachment=False,
        download_name="output.png"
    )

if __name__ == "__main__":
    # Render’in verdiği PORT değerini kullan
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
