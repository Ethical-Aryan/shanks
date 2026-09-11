"""
🏴‍☠️ TIDES OF FORTUNE — All-in-One Flask Backend
Combines video frame extraction, REST API, and static/template serving in a single file.

Usage:
  - Run web server:
      python app.py
  - Extract frames manually via CLI:
      python app.py --extract --video videos/p1.mp4 --frames 160
"""

import os
import sys
import json
import argparse
import base64
import io
import cv2
import numpy as np
from PIL import Image
from flask import Flask, render_template, jsonify, request, send_file
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

# ==========================================
# PATH CONFIGURATION
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Check if running inside 'backend' folder or workspace root
if os.path.basename(BASE_DIR) == 'backend':
    ROOT_DIR = os.path.dirname(BASE_DIR)
    VIDEOS_DIR = os.path.join(BASE_DIR, 'videos')
else:
    ROOT_DIR = BASE_DIR
    VIDEOS_DIR = os.path.join(BASE_DIR, 'backend', 'videos')

FRONTEND_DIR = os.path.join(ROOT_DIR, 'frontend')
STATIC_DIR = os.path.join(FRONTEND_DIR, 'static')
TEMPLATES_DIR = os.path.join(FRONTEND_DIR, 'templates')
FRAMES_DIR = os.path.join(STATIC_DIR, 'frames')
MANIFEST_PATH = os.path.join(FRAMES_DIR, 'manifest.json')

# ==========================================
# FLASK APPLICATION SETUP
# ==========================================
app = Flask(
    __name__,
    static_folder=STATIC_DIR,
    template_folder=TEMPLATES_DIR,
    static_url_path='/static'
)

# ==========================================
# VIDEO FRAME EXTRACTION ENGINE (OpenCV)
# ==========================================
def extract_video_frames(video_filename='p2.webm', target_frames=240, max_width=1920, quality=88, ext="jpg"):
    """
    Slices video into evenly spaced, web-optimized JPEG frames
    and outputs a manifest.json with dimension & pattern metadata.
    """
    # Resolve video path
    video_path = video_filename
    if not os.path.isabs(video_path):
        candidates = [
            os.path.join(VIDEOS_DIR, video_filename),
            os.path.join(BASE_DIR, video_filename),
            os.path.join(ROOT_DIR, video_filename),
            video_filename
        ]
        for c in candidates:
            if os.path.exists(c):
                video_path = c
                break

    if not os.path.exists(video_path):
        print(f"[EXTRACT ERROR] Video file not found: {video_path}")
        return False

    os.makedirs(FRAMES_DIR, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[EXTRACT ERROR] Could not open video: {video_path}")
        return False

    total_video_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    orig_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    orig_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = total_video_frames / video_fps

    num_frames = min(target_frames, total_video_frames)
    frame_indices = np.linspace(0, total_video_frames - 1, num_frames, dtype=int)
    frame_index_set = set(frame_indices)

    # Resolution downscaling
    if orig_w > max_width:
        scale = max_width / orig_w
        target_w = max_width
        target_h = int(orig_h * scale)
    else:
        target_w = orig_w
        target_h = orig_h

    print(f">> [PIRATE VOYAGE] Extracting {num_frames} frames from '{video_path}'...")
    print(f"   Source: {orig_w}x{orig_h} ({total_video_frames} frames @ {video_fps:.1f} fps)")
    print(f"   Target: {target_w}x{target_h} -> '{FRAMES_DIR}'")

    current_idx = 0
    saved_count = 0
    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), quality]

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if current_idx in frame_index_set:
            if target_w != orig_w or target_h != orig_h:
                frame = cv2.resize(frame, (target_w, target_h), interpolation=cv2.INTER_AREA)

            saved_count += 1
            frame_filename_out = f"frame_{saved_count:04d}.{ext}"
            frame_filepath = os.path.join(FRAMES_DIR, frame_filename_out)
            cv2.imwrite(frame_filepath, frame, encode_params)

        current_idx += 1

    cap.release()

    manifest = {
        "videoName": os.path.basename(video_path),
        "totalFrames": saved_count,
        "width": target_w,
        "height": target_h,
        "aspectRatio": round(target_w / target_h, 4) if target_h else 1.7778,
        "duration": round(duration, 2),
        "pattern": f"/static/frames/frame_{{index}}.{ext}",
        "zeroPadding": 4
    }

    with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    print(f"[OK] [PIRATE VOYAGE] Extracted {saved_count} frames successfully into '{FRAMES_DIR}'!\n")
    return True

def ensure_frames_exist():
    """Ensures frames exist in static/frames on server start."""
    needs_extract = True
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            total = manifest.get('totalFrames', 0)
            existing_frames = [f for f in os.listdir(FRAMES_DIR) if f.startswith('frame_') and f.endswith('.jpg')]
            if len(existing_frames) >= total and total > 0:
                needs_extract = False
                print(f"[OK] [PIRATE VOYAGE] Found {len(existing_frames)} existing frames in '{FRAMES_DIR}'. Ready to sail!")
        except Exception as e:
            print(f"[WARN] Error verifying manifest: {e}")

    if needs_extract:
        p2 = os.path.join(VIDEOS_DIR, 'p2.webm')
        if os.path.exists(p2):
            extract_video_frames('p2.webm', target_frames=240, max_width=1920, quality=88)

# ==========================================
# PIRATE CIPHER & CRYPTOGRAPHY (AES & CAESAR)
# ==========================================
def encrypt_aes(message: str, passphrase: str) -> str:
    """Encrypts message with AES-256-GCM using PBKDF2-HMAC-SHA256 key derivation."""
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = kdf.derive(passphrase.encode('utf-8'))
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, message.encode('utf-8'), None)
    payload = salt + nonce + ciphertext
    return 'PIRATE_AES:' + base64.b64encode(payload).decode('utf-8')

def decrypt_aes(token: str, passphrase: str) -> str:
    """Decrypts and authenticates AES-256-GCM encrypted message."""
    if not token.startswith('PIRATE_AES:'):
        raise ValueError('Invalid token header. Expected PIRATE_AES: prefix.')
    data = base64.b64decode(token[len('PIRATE_AES:'):])
    if len(data) < 28:
        raise ValueError('Cursed payload: Token is too short or corrupted.')
    salt = data[:16]
    nonce = data[16:28]
    ciphertext = data[28:]
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = kdf.derive(passphrase.encode('utf-8'))
    aesgcm = AESGCM(key)
    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    except Exception:
        raise ValueError("Shiver me timbers! Invalid pirate passphrase or corrupted cipher payload.")
    return plaintext.decode('utf-8')

def encrypt_caesar(message: str, shift: int = 7) -> str:
    """Encrypts message with classic Caesar / Aztec glyph shift cipher."""
    res = []
    for c in message:
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            res.append(chr((ord(c) - base + shift) % 26 + base))
        else:
            res.append(c)
    payload = f"{shift}:{''.join(res)}"
    return 'PIRATE_CAESAR:' + base64.b64encode(payload.encode('utf-8')).decode('utf-8')

def decrypt_caesar(token: str, key_override: int = None) -> str:
    """Decrypts classic Caesar / Aztec glyph shift cipher."""
    if not token.startswith('PIRATE_CAESAR:'):
        raise ValueError('Invalid token header. Expected PIRATE_CAESAR: prefix.')
    data = base64.b64decode(token[len('PIRATE_CAESAR:'):]).decode('utf-8')
    orig_shift_str, text = data.split(':', 1)
    shift = key_override if key_override is not None else int(orig_shift_str)
    res = []
    for c in text:
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            res.append(chr((ord(c) - base - shift) % 26 + base))
        else:
            res.append(c)
    return ''.join(res)

# ==========================================
# PIRATE STEGANOGRAPHY ENGINE (LSB In Invisible Ink)
# ==========================================
def encode_stego_image(img: Image.Image, message: str, passphrase: str = "") -> Image.Image:
    """Embeds message (optionally encrypted with AES-256) into image using LSB steganography."""
    img = img.convert('RGB')
    payload_str = message
    if passphrase:
        payload_str = encrypt_aes(message, passphrase)

    raw_bytes = payload_str.encode('utf-8')
    magic = b'PIRATE_STEG:'
    length_bytes = len(raw_bytes).to_bytes(4, byteorder='big')
    full_payload = magic + length_bytes + raw_bytes

    bits = np.unpackbits(np.frombuffer(full_payload, dtype=np.uint8))
    arr = np.array(img, dtype=np.uint8)
    flat = arr.reshape(-1)

    if len(bits) > len(flat):
        raise ValueError(f"Secret message is too long ({len(bits)} bits) for this image ({len(flat)} capacity bits). Use a larger image or shorter message.")

    flat[:len(bits)] = (flat[:len(bits)] & 0xFE) | bits
    return Image.fromarray(flat.reshape(arr.shape))

def decode_stego_image(img: Image.Image, passphrase: str = "") -> tuple[str, bool]:
    """Extracts hidden message from image using LSB steganography and decrypts if needed."""
    img = img.convert('RGB')
    arr = np.array(img, dtype=np.uint8)
    flat = arr.reshape(-1)

    # Header: 12 bytes magic ('PIRATE_STEG:') + 4 bytes length = 16 bytes = 128 bits
    if len(flat) < 128:
        raise ValueError("Image is too small to contain a pirate steganographic secret.")

    header_bits = flat[:128] & 1
    header_bytes = np.packbits(header_bits).tobytes()

    if not header_bytes.startswith(b'PIRATE_STEG:'):
        raise ValueError("Avast! No secret pirate steganographic missive was found in this image.")

    msg_len = int.from_bytes(header_bytes[12:16], byteorder='big')
    total_bits = (16 + msg_len) * 8
    if len(flat) < total_bits:
        raise ValueError("Corrupted steganographic payload: Image data was altered, compressed or cropped.")

    payload_bits = flat[128:total_bits] & 1
    extracted_text = np.packbits(payload_bits).tobytes().decode('utf-8', errors='replace')

    was_encrypted = False
    if extracted_text.startswith('PIRATE_AES:'):
        was_encrypted = True
        if not passphrase:
            raise ValueError("This image is sealed with cursed AES encryption! A pirate passphrase is required to decrypt the hidden ink.")
        extracted_text = decrypt_aes(extracted_text, passphrase)

    return extracted_text, was_encrypted

# ==========================================
# WEB ROUTES & API ENDPOINTS
# ==========================================
@app.route('/')
def index():
    """Serves the pirate scrollytelling frontend."""
    return render_template('index.html')

@app.route('/encrypt')
def encrypt_page():
    """Serves the pirate encryption / decryption station."""
    return render_template('encrypt.html')

@app.route('/steganography')
def steganography_page():
    """Serves the pirate image steganography station."""
    return render_template('steganography.html')

@app.route('/attack-simulator')
@app.route('/attack')
def attack_simulator_page():
    """Serves the Dead Man's Cipher real transmission attack simulator."""
    return render_template('attack_simulator.html')

@app.route('/api/transmission/verify', methods=['POST'])
def api_transmission_verify():
    """Receiver verification pipeline for real and attacked transmissions."""
    data = request.get_json() or {}
    msg_id = data.get('messageId', 'UNKNOWN')
    payload = data.get('encryptedPayload', '').strip()
    passphrase = data.get('passphrase', '').strip()
    expected_sha = data.get('expectedSha256', '').strip()

    if not payload:
        return jsonify({
            "success": False,
            "error": "No encrypted payload found in transmission.",
            "authValid": False,
            "sha256Valid": False
        }), 400

    import hashlib
    actual_sha = hashlib.sha256(payload.encode('utf-8')).hexdigest()
    sha_match = (actual_sha.lower() == expected_sha.lower()) if expected_sha else True

    try:
        decrypted_text = decrypt_aes(payload, passphrase)
        return jsonify({
            "success": True,
            "messageId": msg_id,
            "authValid": True,
            "sha256Valid": sha_match,
            "actualSha256": actual_sha,
            "decryptedMessage": decrypted_text
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "messageId": msg_id,
            "authValid": False,
            "sha256Valid": sha_match,
            "actualSha256": actual_sha,
            "error": str(e)
        })

@app.route('/api/stego/encode', methods=['POST'])
def api_stego_encode():
    """Embeds secret text invisibly into an uploaded image."""
    message = request.form.get('message', '').strip()
    passphrase = request.form.get('passphrase', '').strip()
    file = request.files.get('image')

    if not message:
        return jsonify({"success": False, "error": "Avast! Please provide a secret message to hide."}), 400

    try:
        if file and file.filename:
            raw_bytes = file.read()
            if not raw_bytes:
                img = Image.new('RGB', (800, 600), color=(26, 38, 54))
            else:
                img = Image.open(io.BytesIO(raw_bytes))
        else:
            # Generate or use starter parchment map image
            img = Image.new('RGB', (800, 600), color=(26, 38, 54))

        stego_img = encode_stego_image(img, message=message, passphrase=passphrase)

        # Output PNG buffer to prevent lossy compression
        buf = io.BytesIO()
        stego_img.save(buf, format='PNG')
        buf.seek(0)
        b64_img = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode('utf-8')

        return jsonify({
            "success": True,
            "imageUrl": b64_img,
            "width": stego_img.width,
            "height": stego_img.height,
            "wasEncrypted": bool(passphrase)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/stego/decode', methods=['POST'])
def api_stego_decode():
    """Extracts hidden text from an uploaded stego image."""
    passphrase = request.form.get('passphrase', '').strip()
    file = request.files.get('image')

    if not file or not file.filename:
        return jsonify({"success": False, "error": "Avast! Please upload an image to inspect for hidden ink."}), 400

    try:
        raw_bytes = file.read()
        if not raw_bytes:
            return jsonify({"success": False, "error": "Avast! The uploaded file is empty."}), 400
        img = Image.open(io.BytesIO(raw_bytes))
        message, was_encrypted = decode_stego_image(img, passphrase=passphrase)

        return jsonify({
            "success": True,
            "message": message,
            "wasEncrypted": was_encrypted
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route('/api/cipher/encrypt', methods=['POST'])
def api_cipher_encrypt():
    """Encrypts a pirate secret message using AES or Caesar."""
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    key = data.get('key', '').strip()
    algo = data.get('algorithm', 'aes').lower()

    if not message:
        return jsonify({"success": False, "error": "Avast! Secret message cannot be empty."}), 400
    if not key:
        return jsonify({"success": False, "error": "Shiver me timbers! You must provide a secret pirate passphrase."}), 400

    try:
        if algo == 'caesar':
            try:
                shift = int(key) % 26
            except ValueError:
                shift = sum(ord(c) for c in key) % 26 or 7
            token = encrypt_caesar(message, shift=shift)
        else:
            token = encrypt_aes(message, passphrase=key)

        return jsonify({
            "success": True,
            "algorithm": algo.upper(),
            "ciphertext": token,
            "messageLength": len(message)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/cipher/decrypt', methods=['POST'])
def api_cipher_decrypt():
    """Decrypts a sealed pirate missive using AES or Caesar."""
    data = request.get_json() or {}
    token = data.get('ciphertext', '').strip()
    key = data.get('key', '').strip()

    if not token:
        return jsonify({"success": False, "error": "Avast! No sealed ciphertext provided."}), 400
    if not key:
        return jsonify({"success": False, "error": "Provide the pirate passphrase to break the wax seal."}), 400

    try:
        if token.startswith('PIRATE_CAESAR:'):
            try:
                shift = int(key) % 26
            except ValueError:
                shift = sum(ord(c) for c in key) % 26 or 7
            plaintext = decrypt_caesar(token, key_override=shift)
            algo = "CAESAR"
        elif token.startswith('PIRATE_AES:'):
            plaintext = decrypt_aes(token, passphrase=key)
            algo = "AES-256-GCM"
        else:
            # Fallback auto attempt AES
            plaintext = decrypt_aes(token, passphrase=key)
            algo = "AES-256-GCM"

        return jsonify({
            "success": True,
            "algorithm": algo,
            "plaintext": plaintext
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Arrr! Cursed key! The wax seal rejects your passphrase or the missive was tampered with."
        }), 400

@app.route('/api/frames-info')
def get_frames_info():
    """Returns frame metadata manifest for the canvas engine."""
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    return jsonify({
        "videoName": "p2.webm",
        "totalFrames": 240,
        "width": 1920,
        "height": 1080,
        "pattern": "/static/frames/frame_{index}.jpg",
        "zeroPadding": 4
    })

@app.route('/api/extract', methods=['POST'])
def api_extract():
    """Allows extracting frames from video on-demand."""
    data = request.get_json() or {}
    video_file = data.get('video', 'p2.webm')
    frames = int(data.get('frames', 240))
    success = extract_video_frames(video_file, target_frames=frames)
    if success:
        with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
            return jsonify({"success": True, "manifest": json.load(f)})
    return jsonify({"success": False, "error": "Extraction failed"}), 500

@app.route('/api/clash-frames-info')
def get_clash_frames_info():
    """Returns frame metadata manifest for the pirate clash animation."""
    clash_manifest = os.path.join(STATIC_DIR, 'clash_frames', 'manifest.json')
    if os.path.exists(clash_manifest):
        with open(clash_manifest, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    return jsonify({
        "videoName": "piratesclashing.mp4",
        "totalFrames": 240,
        "width": 1280,
        "height": 720,
        "pattern": "/static/clash_frames/frame_{index}.jpg",
        "zeroPadding": 4
    })

@app.after_request
def add_header(response):
    """Aggressive caching for static frames to ensure smooth 60fps scrubbing."""
    if request.path.startswith('/static/frames/') or request.path.startswith('/static/clash_frames/'):
        response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    return response

# ==========================================
# CLI & SERVER ENTRY POINT
# ==========================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Pirate Scrollytelling Backend & Extractor")
    parser.add_argument('--extract', action='store_true', help="Run frame extraction only without starting web server")
    parser.add_argument('--video', type=str, default='p2.webm', help="Video file to extract (default: p2.webm)")
    parser.add_argument('--frames', type=int, default=240, help="Number of frames to extract (default: 240)")
    parser.add_argument('--width', type=int, default=1920, help="Target frame width (default: 1920)")
    parser.add_argument('--quality', type=int, default=88, help="JPEG quality 1-100 (default: 88)")
    parser.add_argument('--port', type=int, default=5000, help="Flask server port (default: 5000)")
    parser.add_argument('--host', type=str, default='0.0.0.0', help="Flask server host (default: 0.0.0.0)")

    args, unknown = parser.parse_known_args()

    if args.extract:
        extract_video_frames(
            video_filename=args.video,
            target_frames=args.frames,
            max_width=args.width,
            quality=args.quality
        )
    else:
        ensure_frames_exist()
        print("\n========================================================")
        print("  🏴‍☠️  TIDES OF FORTUNE: Pirate Scrollytelling Server")
        print(f"  🌊  Running Flask server on http://127.0.0.1:{args.port}")
        print("========================================================\n")
        app.run(host=args.host, port=args.port, debug=True)
