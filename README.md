# 🏴‍☠️ DEAD MAN'S CIPHER & TIDES OF FORTUNE — Pirate Scrollytelling & Security Suite

A cinematic pirate-themed cryptographic voyage and scrollytelling web application featuring Apple-style scroll-driven frame-by-frame animation, AES-256-GCM authenticated encryption, LSB image steganography, and an interactive Man-In-The-Middle (MitM) Attack Simulator with 60fps video frame scrubbing.

---

## 📂 Project Organization

```
hackathon/
├── backend/
│   ├── app.py                 # All-in-one Flask backend & cryptographic engine
│   └── requirements.txt       # Dependencies (flask, cryptography, pillow, opencv-python)
│
├── frontend/
│   ├── templates/
│   │   ├── index.html         # Main scrollytelling voyage (p2.webm frames)
│   │   ├── encrypt.html       # Dual-pirate station: AES-256-GCM & Caesar encryption
│   │   ├── steganography.html # LSB invisible ink sea chart steganography
│   │   └── attack_simulator.html # 3-actor Man-in-the-Middle attack simulator
│   │
│   ├── static/
│   │   ├── css/styles.css     # Pirate theme, responsive rules & custom scrollbars
│   │   ├── js/
│   │   │   ├── config.js      # Scrollytelling configuration & chapters
│   │   │   ├── soundSynth.js  # Web Audio API ambient sea waves & soundboard SFX
│   │   │   └── app.js         # Lenis smooth scroll & 60fps canvas render engine
│   │   ├── frames/            # Extracted 240 frames from p2.webm
│   │   └── clash_frames/      # Extracted 240 frames from piratesclashing.mp4
│
├── piratesclashing.mp4        # Source boarding battle footage
├── run.py                     # Convenience root launcher
└── README.md                  # Project documentation
```

---

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 2. Launch the Application
```bash
python backend/app.py
```
*(Or optionally `python run.py` from root)*

### 3. Open in Browser
Visit **[http://127.0.0.1:5000](http://127.0.0.1:5000)** to embark on the voyage!

- **Voyage Scrollytelling**: `http://127.0.0.1:5000/`
- **Cipher Desk**: `http://127.0.0.1:5000/encrypt`
- **Steganography Studio**: `http://127.0.0.1:5000/steganography`
- **Attack Simulator**: `http://127.0.0.1:5000/attack-simulator`

---

## ⚓ Key Features

1. **Scroll-Driven Frame Animation (PC & Tablet)**:
   - 240-frame sequence powered by Lenis smooth momentum scrolling and high-performance canvas lerp rendering.
   - Dedicated Pirates Clashing boarding battle animation on the Attack Simulator page.
2. **Mobile-Friendly Architecture**:
   - On mobile devices (< 768px), heavy video frames and canvases are cleanly disabled to conserve bandwidth and CPU.
   - Fully responsive UI with touch-friendly controls, adaptive typography, and seamless card stacking.
3. **Dual-Pirate Cipher Desk**:
   - Captain Blackbeard encrypts secret fleet coordinates with AES-256-GCM or Caesar cipher.
   - Quartermaster decrypts authentic missives using shared passphrases.
4. **LSB Invisible Ink Steganography**:
   - Embed and extract secret messages invisibly into sea chart pixels using 1-bit LSB steganography with optional AES-256 seal.
5. **Real-Time MITM Attack Simulator**:
   - Step 1: Captain Blackbeard encrypts secret message and coordinates.
   - Step 2: Middle Interceptor intercepts and modifies the secret message text directly with customizable tampering presets and mode selection (Unauthenticated vs Authenticated AES-GCM).
   - Step 3: Quartermaster inspects the packet, detects forgeries via Galois/Counter Mode GHASH tags or displays modified orders if unprotected.
- **Pirate Audio Synthesizer**: Web Audio API ambient sea waves, creaking timber, port cannon blasts, and clinking gold doubloons.
- **Interactive Story Acts**: Parchment story milestones that fade and float as you scroll through uncharted waters, Siren's maelstrom, and Aztec gold vaults.
- **Doubloon Claim**: Interactive Aztec coin button with golden confetti and coin sound effects.
