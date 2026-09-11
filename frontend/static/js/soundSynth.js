// Atmospheric Web Audio API sound synthesizer for pirate ambiance

class SoundSynth {
  constructor() {
    this.ctx = null;
    this.isPlaying = false;
    this.masterGain = null;
    this.timer = null;
  }

  init() {
    if (this.ctx) return;
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    this.ctx = new AudioContext();
    this.masterGain = this.ctx.createGain();
    this.masterGain.gain.value = 0.35;
    this.masterGain.connect(this.ctx.destination);
  }

  startAmbient() {
    this.init();
    if (this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
    if (this.isPlaying) return;
    this.isPlaying = true;

    // Ocean Waves Pink Noise
    const bufferSize = this.ctx.sampleRate * 2;
    const noiseBuffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
    const output = noiseBuffer.getChannelData(0);
    let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0;
    for (let i = 0; i < bufferSize; i++) {
      const white = Math.random() * 2 - 1;
      b0 = 0.99886 * b0 + white * 0.0555179;
      b1 = 0.99332 * b1 + white * 0.0750759;
      b2 = 0.96900 * b2 + white * 0.1538520;
      b3 = 0.86650 * b3 + white * 0.3104856;
      b4 = 0.55000 * b4 + white * 0.5329522;
      b5 = -0.7616 * b5 - white * 0.0168980;
      output[i] = b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362;
      output[i] *= 0.11;
      b6 = white * 0.115926;
    }

    const whiteNoise = this.ctx.createBufferSource();
    whiteNoise.buffer = noiseBuffer;
    whiteNoise.loop = true;

    const filter = this.ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.value = 380;

    // LFO for surf roll
    const lfo = this.ctx.createOscillator();
    lfo.frequency.value = 0.14;
    const lfoGain = this.ctx.createGain();
    lfoGain.gain.value = 300;
    lfo.connect(filter.frequency);

    const waveGain = this.ctx.createGain();
    waveGain.gain.value = 0.28;

    whiteNoise.connect(filter);
    filter.connect(waveGain);
    waveGain.connect(this.masterGain);

    whiteNoise.start();
    lfo.start();

    this.scheduleCreaks();
  }

  scheduleCreaks() {
    if (!this.isPlaying) return;
    const delay = Math.random() * 6000 + 4000;
    this.timer = setTimeout(() => {
      if (this.isPlaying) {
        this.playCreak();
        this.scheduleCreaks();
      }
    }, delay);
  }

  playCreak() {
    if (!this.ctx || this.ctx.state === 'suspended') return;
    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sawtooth';
      const now = this.ctx.currentTime;
      osc.frequency.setValueAtTime(85 + Math.random() * 35, now);
      osc.frequency.exponentialRampToValueAtTime(45 + Math.random() * 20, now + 0.8);

      gain.gain.setValueAtTime(0.01, now);
      gain.gain.linearRampToValueAtTime(0.04, now + 0.2);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.8);

      const filter = this.ctx.createBiquadFilter();
      filter.type = 'bandpass';
      filter.frequency.value = 240;

      osc.connect(filter);
      filter.connect(gain);
      gain.connect(this.masterGain);

      osc.start(now);
      osc.stop(now + 0.9);
    } catch (e) {}
  }

  playCoinClink() {
    this.init();
    if (this.ctx.state === 'suspended') this.ctx.resume();
    const now = this.ctx.currentTime;

    [1800, 2400, 3200].forEach((freq, idx) => {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(freq + Math.random() * 80, now + idx * 0.04);

      gain.gain.setValueAtTime(0.12, now + idx * 0.04);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + idx * 0.04 + 0.45);

      osc.connect(gain);
      gain.connect(this.masterGain);
      osc.start(now + idx * 0.04);
      osc.stop(now + idx * 0.04 + 0.5);
    });
  }

  playCannon() {
    this.init();
    if (this.ctx.state === 'suspended') this.ctx.resume();
    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = 'triangle';
    osc.frequency.setValueAtTime(160, now);
    osc.frequency.exponentialRampToValueAtTime(30, now + 0.7);

    gain.gain.setValueAtTime(0.4, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.8);

    osc.connect(gain);
    gain.connect(this.masterGain);
    osc.start(now);
    osc.stop(now + 0.85);
  }

  stop() {
    this.isPlaying = false;
    if (this.timer) clearTimeout(this.timer);
    if (this.ctx && this.ctx.state !== 'closed') {
      this.ctx.suspend();
    }
  }
}

window.soundSynth = new SoundSynth();
