// Pirate Scrollytelling Engine with Smooth Inertial Lerp and Canvas Scrubbing

(function() {
  'use strict';

  const config = window.PIRATE_CONFIG || {
    apiEndpoint: '/api/frames-info',
    defaultFrames: 160,
    lerpFactor: 0.12
  };

  // State
  let images = [];
  let totalFrames = config.defaultFrames;
  let currentLerpFrame = 0;
  let targetFrame = 0;
  let lastDrawnFrame = -1;
  let scrollProgress = 0;
  let isAudioPlaying = false;
  let lenisInstance = null;

  // DOM Elements
  const canvas = document.getElementById('scrolly-canvas');
  const ctx = canvas ? canvas.getContext('2d') : null;
  const loadingOverlay = document.getElementById('loading-overlay');
  const loadingProgress = document.getElementById('loading-progress');
  const loadingText = document.getElementById('loading-text');
  const loadingCount = document.getElementById('loading-count');
  const compassNeedle = document.getElementById('compass-needle');
  const hudFrameDisplay = document.getElementById('hud-frame-display');
  const hudDepth = document.getElementById('hud-depth');
  const hudKnots = document.getElementById('hud-knots');
  const audioToggleBtn = document.getElementById('audio-toggle-btn');
  const audioStatusText = document.getElementById('audio-status-text');

  // Story Elements
  const stages = {
    hero: document.getElementById('stage-hero'),
    act1: document.getElementById('stage-act1'),
    act2: document.getElementById('stage-act2'),
    act3: document.getElementById('stage-act3'),
    epilogue: document.getElementById('stage-epilogue')
  };

  // 1. Initialize Lenis Smooth Scrolling for buttery momentum
  function initSmoothScroll() {
    if (typeof Lenis !== 'undefined') {
      lenisInstance = new Lenis({
        duration: 1.2,
        easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
        orientation: 'vertical',
        gestureOrientation: 'vertical',
        smoothWheel: true,
        wheelMultiplier: 0.85,
        touchMultiplier: 1.5,
      });

      function raf(time) {
        lenisInstance.raf(time);
        requestAnimationFrame(raf);
      }
      requestAnimationFrame(raf);

      lenisInstance.on('scroll', onScrollEvent);
    } else {
      window.addEventListener('scroll', onScrollEvent, { passive: true });
    }
  }

  // 2. Fetch Manifest & Preload Frames
  async function loadFrames() {
    // Mobile Rule: If mobile (< 768px), do not load video frames or show loading overlay
    if (window.innerWidth < 768) {
      if (loadingOverlay) loadingOverlay.style.display = 'none';
      console.log('[AppEngine] Mobile view detected (<768px): Video frames disabled.');
      return;
    }

    try {
      const res = await fetch(config.apiEndpoint);
      if (res.ok) {
        const manifest = await res.json();
        totalFrames = manifest.totalFrames || config.defaultFrames;
      }
    } catch (e) {
      console.warn('Could not fetch frames manifest from Flask API, using default:', e);
    }

    images = new Array(totalFrames);
    let loadedCount = 0;

    const updateProgress = () => {
      loadedCount++;
      const pct = Math.round((loadedCount / totalFrames) * 100);
      if (loadingProgress) loadingProgress.style.width = `${pct}%`;
      if (loadingText) loadingText.textContent = `${pct}% LOADED`;
      if (loadingCount) loadingCount.textContent = `(${loadedCount}/${totalFrames})`;

      if (loadedCount === totalFrames) {
        setTimeout(() => {
          if (loadingOverlay) {
            loadingOverlay.classList.add('opacity-0', 'pointer-events-none');
            setTimeout(() => loadingOverlay.style.display = 'none', 500);
          }
          // Draw first frame immediately
          drawFrame(0);
        }, 300);
      }
    };

    for (let i = 1; i <= totalFrames; i++) {
      const numStr = String(i).padStart(4, '0');
      const src = `/static/frames/frame_${numStr}.jpg`;
      const img = new Image();
      img.src = src;

      img.onload = () => {
        // Attempt pre-decoding for zero main-thread lag
        if (img.decode) {
          img.decode().then(updateProgress).catch(updateProgress);
        } else {
          updateProgress();
        }
      };
      img.onerror = updateProgress;
      images[i - 1] = img;
    }
  }

  // 3. Scroll progress computation
  function onScrollEvent() {
    const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
    const scrollTop = window.scrollY || window.pageYOffset;
    scrollProgress = Math.max(0, Math.min(1, scrollTop / (scrollHeight || 1)));

    targetFrame = scrollProgress * (totalFrames - 1);

    updateTelemetryHUD();
    updateStoryMilestones();
  }

  // 4. Update HUD Telemetry & Compass
  function updateTelemetryHUD() {
    const degrees = Math.round(scrollProgress * 360 * 2.5);
    if (compassNeedle) {
      compassNeedle.style.transform = `rotate(${degrees}deg)`;
    }

    const depth = Math.round(12 + scrollProgress * 180);
    const knots = (6.5 + Math.sin(scrollProgress * Math.PI) * 4.2).toFixed(1);
    if (hudDepth) hudDepth.textContent = `${depth} fm`;
    if (hudKnots) hudKnots.textContent = `${knots} kts`;

    const displayIdx = Math.min(totalFrames, Math.max(1, Math.round(currentLerpFrame) + 1));
    if (hudFrameDisplay) {
      hudFrameDisplay.textContent = `FRAME ${String(displayIdx).padStart(3, '0')} / ${totalFrames}`;
    }
  }

  // 5. Update Story Stages with smooth opacity & translation
  function updateStoryMilestones() {
    applyStageTransform(stages.hero, 0.0, 0.16, 0.0, 0.10);
    applyStageTransform(stages.act1, 0.18, 0.42, 0.25, 0.35);
    applyStageTransform(stages.act2, 0.44, 0.68, 0.50, 0.60);
    applyStageTransform(stages.act3, 0.68, 0.92, 0.74, 0.86);
    applyStageTransform(stages.epilogue, 0.90, 1.0, 0.94, 1.0);
  }

  function applyStageTransform(el, start, end, peakStart, peakEnd) {
    if (!el) return;
    if (scrollProgress < start || scrollProgress > end) {
      el.style.opacity = '0';
      el.style.pointerEvents = 'none';
      el.style.transform = 'translateY(24px) scale(0.96)';
      return;
    }

    let opacity = 1;
    if (scrollProgress < peakStart) {
      opacity = (scrollProgress - start) / (peakStart - start);
    } else if (scrollProgress > peakEnd) {
      opacity = 1 - (scrollProgress - peakEnd) / (end - peakEnd);
    }
    opacity = Math.max(0, Math.min(1, opacity));
    const translateY = (1 - opacity) * 20;

    el.style.opacity = opacity.toFixed(3);
    el.style.pointerEvents = opacity > 0.35 ? 'auto' : 'none';
    el.style.transform = `translateY(${translateY.toFixed(1)}px) scale(${(0.96 + opacity * 0.04).toFixed(3)})`;
  }

  // 6. High-Performance Canvas Rendering Loop
  function renderLoop() {
    if (window.innerWidth < 768) return; // Skip on mobile

    // Silky lerp interpolation
    const diff = targetFrame - currentLerpFrame;
    currentLerpFrame += diff * config.lerpFactor;

    const frameIdx = Math.round(currentLerpFrame);
    const clampedIdx = Math.max(0, Math.min(totalFrames - 1, frameIdx));

    if (clampedIdx !== lastDrawnFrame && images[clampedIdx]) {
      drawFrame(clampedIdx);
      lastDrawnFrame = clampedIdx;
      updateTelemetryHUD();
    }

    requestAnimationFrame(renderLoop);
  }

  function drawFrame(idx) {
    if (!ctx || !images[idx]) return;
    const img = images[idx];
    if (!img.complete || img.naturalWidth === 0) return;

    const dpr = window.devicePixelRatio || 1;
    const renderW = canvas.width / dpr;
    const renderH = canvas.height / dpr;

    ctx.save();
    ctx.scale(dpr, dpr);

    // Compute 'cover' aspect ratio
    const imgRatio = img.naturalWidth / img.naturalHeight;
    const canvasRatio = renderW / renderH;

    let drawW, drawH, offsetX, offsetY;
    if (canvasRatio > imgRatio) {
      drawW = renderW;
      drawH = renderW / imgRatio;
      offsetX = 0;
      offsetY = (renderH - drawH) / 2;
    } else {
      drawH = renderH;
      drawW = renderH * imgRatio;
      offsetX = (renderW - drawW) / 2;
      offsetY = 0;
    }

    ctx.fillStyle = '#02060d';
    ctx.fillRect(0, 0, renderW, renderH);
    ctx.drawImage(img, offsetX, offsetY, drawW, drawH);
    ctx.restore();
  }

  // 7. Responsive Canvas Resizing with Retina DPR
  function resizeCanvas() {
    if (!canvas) return;
    const dpr = window.devicePixelRatio || 1;
    const w = window.innerWidth;
    const h = window.innerHeight;

    canvas.width = w * dpr;
    canvas.height = h * dpr;
    canvas.style.width = `${w}px`;
    canvas.style.height = `${h}px`;

    lastDrawnFrame = -1; // Force redraw
  }

  // 8. Interactive Events (Audio, Modals, Confetti)
  function initInteractions() {
    // Audio Toggle
    if (audioToggleBtn) {
      audioToggleBtn.addEventListener('click', () => {
        if (!window.soundSynth) return;
        if (isAudioPlaying) {
          window.soundSynth.stop();
          isAudioPlaying = false;
          if (audioStatusText) audioStatusText.textContent = 'Audio: OFF';
          audioToggleBtn.classList.remove('border-doubloon-400');
        } else {
          window.soundSynth.startAmbient();
          isAudioPlaying = true;
          if (audioStatusText) audioStatusText.textContent = 'Audio: ON';
          audioToggleBtn.classList.add('border-doubloon-400');
        }
      });
    }

    // Claim Doubloon Button
    const claimBtn = document.getElementById('claim-doubloon-btn');
    if (claimBtn) {
      claimBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        if (window.soundSynth) window.soundSynth.playCoinClink();
        if (typeof confetti === 'function') {
          confetti({
            particleCount: 85,
            spread: 75,
            origin: { y: 0.65 },
            colors: ['#ffd700', '#f59e0b', '#d97706', '#ffe066', '#ffffff'],
            shapes: ['circle'],
            scalar: 1.2
          });
        }
      });
    }

    // Modals
    const logModal = document.getElementById('log-modal');
    const openLogBtn = document.getElementById('open-log-btn');
    const closeLogBtn = document.getElementById('close-log-btn');
    const closeLogBtn2 = document.getElementById('close-log-btn-2');

    if (openLogBtn && logModal) {
      openLogBtn.addEventListener('click', () => logModal.classList.remove('hidden'));
    }
    const closeLog = () => logModal && logModal.classList.add('hidden');
    if (closeLogBtn) closeLogBtn.addEventListener('click', closeLog);
    if (closeLogBtn2) closeLogBtn2.addEventListener('click', closeLog);

    // Soundboard buttons in modal
    const cannonBtn = document.getElementById('sfx-cannon');
    if (cannonBtn) cannonBtn.addEventListener('click', () => window.soundSynth && window.soundSynth.playCannon());
    const coinBtn = document.getElementById('sfx-coin');
    if (coinBtn) coinBtn.addEventListener('click', () => window.soundSynth && window.soundSynth.playCoinClink());
    const creakBtn = document.getElementById('sfx-creak');
    if (creakBtn) creakBtn.addEventListener('click', () => window.soundSynth && window.soundSynth.playCreak());

    // Scroll to Top buttons
    const scrollToTopBtn = document.getElementById('scroll-top-btn');
    if (scrollToTopBtn) {
      scrollToTopBtn.addEventListener('click', () => {
        if (lenisInstance) {
          lenisInstance.scrollTo(0, { duration: 1.8 });
        } else {
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }
      });
    }
  }

  // Lifecycle initialization
  window.addEventListener('resize', resizeCanvas);
  window.addEventListener('DOMContentLoaded', () => {
    resizeCanvas();
    initSmoothScroll();
    initInteractions();
    loadFrames();
    requestAnimationFrame(renderLoop);
  });

})();
