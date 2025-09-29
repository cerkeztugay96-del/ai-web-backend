from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
from PIL import Image
import io, os, threading

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False, methods=["GET","POST","OPTIONS"])

@app.after_request
def add_cors_headers(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, Accept, Origin"
    return resp

# ---- Model ayarları (GPU arama yok) ----
os.environ.setdefault("U2NET_HOME", "/opt/render/.u2net")
os.environ["CUDA_VISIBLE_DEVICES"] = ""  # GPU’yu tamamen devre dışı bırak
from rembg import new_session, remove

SESSION = None
SESSION_LOCK = threading.Lock()

def get_session():
    global SESSION
    if SESSION is None:
        with SESSION_LOCK:
            if SESSION is None:
                # küçük model + sadece CPU
                SESSION = new_session("u2netp", providers=["CPUExecutionProvider"])
    return SESSION

def warmup_async():
    try:
        get_session()  # model indirilir ama porta bağlanmayı engellemez
    except Exception as e:
        # sadece log için; servis çalışmaya devam eder
        print("Warmup error:", e, flush=True)

@app.route("/", methods=["GET"])
def home():
    # ilk GET’te arkada 1 kez warmup başlat
    threading.Thread(target=warmup_async, daemon=True).start()
    return jsonify({"status": "Backend calisiyor"}), 200

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
        session = get_session()
        img_out = remove(img_in, session=session)

        buf = io.BytesIO()
        img_out.save(buf, format="PNG")
        buf.seek(0)
        return send_file(buf, mimetype="image/png")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
