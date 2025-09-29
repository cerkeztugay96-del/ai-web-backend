from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
from PIL import Image
import io, os

# -------------------------------------------------
# UYGULAMA
# -------------------------------------------------
app = Flask(__name__)

# CORS'u uygulama genelinde aç: Netlify origin’i + gerekirse tüm origin'ler
# Not: '*' en kolayı. Güvenlik istersen Netlify domainini yazabilirsin.
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=False,
    methods=["GET", "POST", "OPTIONS"],
)

# Tüm yanıtlara CORS header'larını garanti ekleyelim (hata sayfaları dahil)
@app.after_request
def add_cors_headers(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, Accept, Origin"
    return resp


# -------------------------------------------------
# SAĞLIK / KÖK
# -------------------------------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Backend calisiyor"}), 200


# -------------------------------------------------
# ARKA PLAN KALDIR — CORS PRELİGHT + GET + POST
# -------------------------------------------------

# Preflight için explicit OPTIONS: 204 döner, CORS header'ları after_request ile eklenecek
@app.route("/arka-plan-kaldir", methods=["OPTIONS"])
def arka_plan_kaldir_options():
    return make_response(("", 204))

# GET ile test etmek istersen 200 döndürsün (404 yerine)
@app.route("/arka-plan-kaldir", methods=["GET"])
def arka_plan_kaldir_get():
    return jsonify({"ok": True, "use": "POST with form-data field 'file'"}), 200

# Asıl işlem: POST
@app.route("/arka-plan-kaldir", methods=["POST"])
def arka_plan_kaldir_post():
    if "file" not in request.files:
        return jsonify({"error": "Dosya yuklenmedi", "hint": "form-data alan adi 'file' olmali"}), 400

    file = request.files["file"]

    try:
        # Ağır importu burada yap (sunucu porta hemen bağlansın)
        from rembg import remove

        # Görseli yükle ve RGBA'ya çevir
        input_image = Image.open(file.stream).convert("RGBA")

        # Arka planı kaldır
        output_image = remove(input_image)

        # Çıktıyı belleğe PNG yaz
        buf = io.BytesIO()
        output_image.save(buf, format="PNG")
        buf.seek(0)

        return send_file(buf, mimetype="image/png")
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------------------------------
# RENDER PORT BIND
# -------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
