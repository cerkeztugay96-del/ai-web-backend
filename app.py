from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
from PIL import Image
import io, os

# ------------ CORS & App ------------
app = Flask(__name__)
# Gerekirse origins'e Netlify alanını da yazabilirsin; '*' pratik ve yeterli
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False, methods=["GET", "POST", "OPTIONS"])

@app.after_request
def add_cors_headers(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, Accept, Origin"
    return resp

# ------------ Model (küçük ve hızlı) ------------
# Büyük model (u2net ~176MB) yerine küçük model (u2netp ~4.7MB)
# Model cache klasörü; Render'da kalıcı diske yazılması için
os.environ.setdefault("U2NET_HOME", "/opt/render/.u2net")
os.makedirs(os.environ["U2NET_HOME"], exist_ok=True)

# Session'ı başta yükle ki ilk istekte indirme beklemeyelim
from rembg import new_session, remove
SESSION = new_session("u2netp")  # küçük, hızlı, RAM dostu

# ------------ Sağlık kontrolü ------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Backend calisiyor"}), 200

# ------------ Preflight / GET / POST ------------
@app.route("/arka-plan-kaldir", methods=["OPTIONS"])
def arka_plan_kaldir_options():
    return make_response(("", 204))

@app.route("/arka-plan-kaldir", methods=["GET"])
def arka_plan_kaldir_get():
    return jsonify({"ok": True, "use": "POST form-data 'file'"}), 200

@app.route("/arka-plan-kaldir", methods=["POST"])
def arka_plan_kaldir_post():
    if "file" not in request.files:
        return jsonify({"error": "Dosya yuklenmedi", "hint": "form-data alan adi 'file' olmali"}), 400
    try:
        file = request.files["file"]
        img_in = Image.open(file.stream).convert("RGBA")
        img_out = remove(img_in, session=SESSION)

        buf = io.BytesIO()
        img_out.save(buf, format="PNG")
        buf.seek(0)
        return send_file(buf, mimetype="image/png")
    except Exception as e:
        # Hata olursa anlaşılır mesaj
        return jsonify({"error": str(e)}), 500

# ------------ Render port bind ------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
