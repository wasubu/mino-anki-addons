(() => {
  // === FIREWORKS CONFIGURATION ===
  const FIREWORK_SETTINGS = {
    baseSpeed: 100,                // Base speed reference (affects relative motion)
    rocketSpeed: 1.0,              // Multiplier for rocket ascent speed
    explosionParticleCount: 60,   // Number of particles per explosion
    explosionParticleSpeed: 1.5,  // How far explosion particles travel
    explosionParticleRadius: 1.0, // How large the explosion particles are
    gravity: 0.1,                  // Downward acceleration on explosion particles
    airResistance: 0.98,          // Friction for explosion particle velocity
    fadeRate: 0.015,              // Rate at which explosion particles fade out
    rocketFadeStart: 0.7,         // Rocket fade begins at 70% ascent
    rocketFadeDuration: 0.3,      // Duration of rocket fade before explosion
    rocketCount: 25,              // Total number of rockets launched
    rocketInterval: 400,          // Delay (ms) between rocket launches
    colors: ['#ff4b4b', '#ffd93d', '#4bffa5', '#3da9ff', '#f64eff'] // Firework colors
  };

  // Explosion sound file path (adjust if needed)
  const explosionSoundPath = "C:/Users/delma/AppData/Roaming/Anki2/addons21/231569866/user_files/themes/Mycustom/sounds/explotions/explode.mp3";
  const explosionAudio = new Audio(explosionSoundPath);

  function hexToRgb(hex) {
    const bigint = parseInt(hex.slice(1), 16);
    const r = (bigint >> 16) & 255;
    const g = (bigint >> 8) & 255;
    const b = bigint & 255;
    return `${r}, ${g}, ${b}`;
  }

  function createFireworksCanvas() {
    const canvas = document.createElement('canvas');
    canvas.id = 'fireworks-canvas';
    Object.assign(canvas.style, {
      position: 'fixed',
      top: '0',
      left: '0',
      width: '100vw',
      height: '100vh',
      pointerEvents: 'none',
      zIndex: '9997'
    });
    document.body.appendChild(canvas);
    return canvas;
  }

  function easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
  }

  class Rocket {
    constructor(canvas, colors) {
      this.canvas = canvas;
      this.ctx = canvas.getContext('2d');
      this.x = Math.random() * canvas.width * 0.8 + canvas.width * 0.1;
      this.yStart = canvas.height;
      this.y = this.yStart;
      this.targetY = Math.random() * canvas.height * 0.5 + canvas.height * 0.1;
      this.totalTravel = this.yStart - this.targetY;
      this.progress = 0;
      this.speed = (0.015 + Math.random() * 0.01) * (FIREWORK_SETTINGS.rocketSpeed * 100 / FIREWORK_SETTINGS.baseSpeed);
      this.colorSet = Math.random() < 0.5
        ? [colors[Math.floor(Math.random() * colors.length)]]
        : [
            colors[Math.floor(Math.random() * colors.length)],
            colors[Math.floor(Math.random() * colors.length)]
          ];
      this.exploded = false;
      this.particles = [];
      this.alpha = 1;
    }

    update() {
      if (!this.exploded) {
        this.progress += this.speed;
        if (this.progress > 1) this.progress = 1;

        const easedProgress = easeOutCubic(this.progress);
        this.y = this.yStart - this.totalTravel * easedProgress;
        this.x += Math.sin(this.y / 20) * 0.5;

        if (this.progress > FIREWORK_SETTINGS.rocketFadeStart) {
          const fadeProgress = (this.progress - FIREWORK_SETTINGS.rocketFadeStart) / FIREWORK_SETTINGS.rocketFadeDuration;
          this.alpha = 1 - Math.min(fadeProgress, 1);
        }

        if (this.progress >= 1) {
          this.explode();
        }
      } else {
        for (let i = this.particles.length - 1; i >= 0; i--) {
          const p = this.particles[i];
          p.vx *= FIREWORK_SETTINGS.airResistance;
          p.vy += FIREWORK_SETTINGS.gravity;
          p.x += p.vx;
          p.y += p.vy;
          p.alpha -= FIREWORK_SETTINGS.fadeRate;
          if (p.alpha <= 0) this.particles.splice(i, 1);
        }
      }
    }

    explode() {
      this.exploded = true;

      // Play explosion sound (clone to allow overlap)
      const soundClone = explosionAudio.cloneNode();
      soundClone.play().catch(e => console.warn('Explosion sound failed to play:', e));

      for (let i = 0; i < FIREWORK_SETTINGS.explosionParticleCount; i++) {
        const angle = Math.random() * 2 * Math.PI;
        const speed = (Math.random() * 4 + 1) * FIREWORK_SETTINGS.explosionParticleSpeed;
        const color = this.colorSet.length === 1
          ? this.colorSet[0]
          : this.colorSet[Math.floor(Math.random() * this.colorSet.length)];

        this.particles.push({
          x: this.x,
          y: this.y,
          vx: Math.cos(angle) * speed,
          vy: Math.sin(angle) * speed,
          radius: (Math.random() * 2 + 1) * FIREWORK_SETTINGS.explosionParticleRadius,
          alpha: 1,
          color
        });
      }
    }

    draw() {
      const ctx = this.ctx;
      if (!this.exploded) {
        ctx.beginPath();
        ctx.arc(this.x, this.y, 3, 0, 2 * Math.PI);
        ctx.fillStyle = `rgba(${hexToRgb(this.colorSet[0])}, ${this.alpha})`;
        ctx.fill();
      } else {
        this.particles.forEach(p => {
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.radius, 0, 2 * Math.PI);
          ctx.fillStyle = `rgba(${hexToRgb(p.color)}, ${p.alpha})`;
          ctx.fill();
        });
      }
    }

    isDone() {
      return this.exploded && this.particles.length === 0;
    }
  }

  function launchFireworks() {
    const canvas = createFireworksCanvas();
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    window.addEventListener('resize', () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    });

    const rockets = [];
    let launchCount = 0;

    const launchInterval = setInterval(() => {
      rockets.push(new Rocket(canvas, FIREWORK_SETTINGS.colors));
      launchCount++;
      if (launchCount >= FIREWORK_SETTINGS.rocketCount) {
        clearInterval(launchInterval);
      }
    }, FIREWORK_SETTINGS.rocketInterval);

    function animate() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      for (let i = rockets.length - 1; i >= 0; i--) {
        rockets[i].update();
        rockets[i].draw();
        if (rockets[i].isDone()) {
          rockets.splice(i, 1);
        }
      }

      if (rockets.length > 0 || launchCount < FIREWORK_SETTINGS.rocketCount) {
        requestAnimationFrame(animate);
      } else {
        canvas.remove();
      }
    }

    animate();
  }

  function onLoad() {
  const div = document.createElement('div');
  div.id = 'avf-img-container';

  const img = document.createElement('img');
  img.id = 'avf-img';

  window.pycmd?.('audiovisualFeedback#randomFile#images/congrats', (src) => {
    if (src == null) {
      console.log('No image source returned from pycmd');
      return;
    }
    console.log('Image source received:', src);
    img.src = src;
    div.appendChild(img);
    document.body.insertBefore(div, document.body.firstChild);
  });

  const audioPath = "C:\\Users\\delma\\AppData\\Roaming\\Anki2\\addons21\\231569866\\user_files\\themes\\Mycustom\\sounds\\explotions\\explode.mp3";
  console.log('Creating audio element with source:', audioPath);
  const applause = new Audio(audioPath);

  applause.addEventListener('canplaythrough', () => {
    console.log('Audio can play through, starting playback');
    applause.play().catch(e => console.warn('Sound failed to play:', e));
  });

  applause.addEventListener('error', (e) => {
    console.error('Audio error event:', e);
  });

  applause.load();

  launchFireworks();
  }
})();