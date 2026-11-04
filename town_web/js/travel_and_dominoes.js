import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';

// Pentatonic Audio Synthesizer for rhythmic chime sounds
class ToyChimeAudio {
  constructor() {
    this.ctx = null;
    this.scale = [261.63, 293.66, 329.63, 392.00, 440.00, 523.25, 587.33, 659.25]; // C Major pentatonic
  }

  init() {
    if (!this.ctx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioContext();
    }
    if (this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  playDing(index) {
    this.init();
    if (!this.ctx) return;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    const freq = this.scale[index % this.scale.length];

    osc.type = 'triangle'; // Sweet bell tone
    osc.frequency.setValueAtTime(freq, this.ctx.currentTime);

    gain.gain.setValueAtTime(0.2, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.35);

    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start();
    osc.stop(this.ctx.currentTime + 0.35);
  }
}

export class TravelAndDominoManager {
  constructor(camera, avatar, scene) {
    this.camera = camera;
    this.avatar = avatar;
    this.scene = scene;
    this.travelMode = 'run'; // 'run' or 'fly'
    this.activeDominoes = [];
    this.audio = new ToyChimeAudio();
    this.isTraveling = false;
  }

  setMode(mode) {
    this.travelMode = mode;
  }

  // Disney-Style Animated Travel: Short, Rhythmic, Stable Camera
  travelTo(targetWorld, onArrival) {
    if (this.isTraveling) return;
    this.isTraveling = true;
    this.audio.init();

    const startPos = this.avatar.position.clone();
    const endPos = new THREE.Vector3(...targetWorld.pos);
    const duration = this.travelMode === 'fly' ? 2200 : 2600; // Snappy 2.5s journey
    const startTime = performance.now();

    const lookTarget = new THREE.Vector3();

    const step = (now) => {
      const t = Math.min((now - startTime) / duration, 1.0);
      
      // Disney Smoothstep Ease-In-Out
      const ease = t * t * (3 - 2 * t);

      // Interpolate horizontal position
      this.avatar.position.x = THREE.MathUtils.lerp(startPos.x, endPos.x, ease);
      this.avatar.position.z = THREE.MathUtils.lerp(startPos.z, endPos.z, ease);

      if (this.travelMode === 'fly') {
        // High playful glide with squash-stretch wings
        const flyArc = Math.sin(t * Math.PI);
        this.avatar.position.y = flyArc * 26 + 1.5;
        this.avatar.scale.set(1.15, 0.85, 1.15); // Stretched gliding shape
        this.avatar.rotation.z = Math.sin(t * Math.PI * 4) * 0.12; // Bank wings
      } else {
        // Disney Character Hop: Bouncing arcs with ground squash
        const hopCycle = Math.sin(t * Math.PI * 8);
        const hopHeight = Math.max(0, hopCycle) * 3.8;
        this.avatar.position.y = hopHeight;

        // Squash on landing, stretch in air
        if (hopHeight < 0.3) {
          this.avatar.scale.set(1.22, 0.78, 1.22); // Squash on ground
        } else {
          this.avatar.scale.set(0.88, 1.18, 0.88); // Stretch during hop
        }
        this.avatar.rotation.z = 0;
      }

      // Turn character smoothly toward destination
      const angle = Math.atan2(endPos.x - startPos.x, endPos.z - startPos.z);
      this.avatar.rotation.y = angle;

      // FIXED Third-Person Camera: Maintains strict offset, avoids disorienting spins
      this.camera.position.set(
        this.avatar.position.x,
        this.avatar.position.y + 16,
        this.avatar.position.z + 32
      );
      lookTarget.set(this.avatar.position.x, this.avatar.position.y + 3, this.avatar.position.z);
      this.camera.lookAt(lookTarget);

      if (t < 1.0) {
        requestAnimationFrame(step);
      } else {
        // Disney Bounce Settle
        this.avatar.position.y = 0;
        this.avatar.scale.set(1, 1, 1);
        this.avatar.rotation.z = 0;
        this.isTraveling = false;
        this.triggerToyDominoShow(targetWorld.pos, onArrival);
      }
    };

    requestAnimationFrame(step);
  }

  // Generates Toy-box Variety Dominoes: Triangles, Cylinders, Shapes, Letters & Numbers
  triggerToyDominoShow(centerPos, onFinish) {
    this.activeDominoes.forEach(d => this.scene.remove(d.mesh));
    this.activeDominoes = [];

    const count = 30;
    const kinds = ['box', 'cylinder', 'triangle', 'ball_topper'];
    const alphabet = ['A', 'B', 'C', '1', '2', '3', '★', '♥'];

    for (let i = 0; i < count; i++) {
      const kind = kinds[i % kinds.length];
      let geo;

      if (kind === 'box') {
        geo = new THREE.BoxGeometry(2.2, 5.5, 0.8);
      } else if (kind === 'cylinder') {
        geo = new THREE.CylinderGeometry(1.2, 1.2, 5.2, 16);
      } else if (kind === 'triangle') {
        geo = new THREE.ConeGeometry(1.8, 5.4, 3);
      } else {
        geo = new THREE.CylinderGeometry(1, 1.4, 4.6, 12);
      }

      // Vibrant candy colors (Disney palette)
      const hue = (i * 0.11) % 1.0;
      const mat = new THREE.MeshStandardMaterial({
        color: new THREE.Color().setHSL(hue, 0.9, 0.6),
        roughness: 0.25
      });

      const domino = new THREE.Mesh(geo, mat);

      // Playful gentle S-curve track
      const t = i / count;
      const x = centerPos[0] + Math.sin(t * Math.PI * 3) * 12;
      const z = centerPos[2] + (t * 40 - 20);

      domino.position.set(x, 2.7, z);
      domino.rotation.y = Math.cos(t * Math.PI * 3) * 0.7;

      this.scene.add(domino);
      this.activeDominoes.push({ mesh: domino, baseRotX: domino.rotation.x });
    }

    // Rhythmic cascade with synchronized chime sounds
    let idx = 0;
    const interval = setInterval(() => {
      if (idx >= this.activeDominoes.length) {
        clearInterval(interval);
        if (onFinish) onFinish();
        return;
      }

      const d = this.activeDominoes[idx];
      this.audio.playDing(idx);

      const startT = performance.now();
      const topple = (now) => {
        const p = Math.min((now - startT) / 140, 1.0);
        d.mesh.rotation.x = d.baseRotX + p * 1.35;
        if (p < 1.0) requestAnimationFrame(topple);
      };
      requestAnimationFrame(topple);
      idx++;
    }, 70); // 70ms rhythmic cadence
  }
}
