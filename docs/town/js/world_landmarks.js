import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';

// Tightened radii (140 - 180 units) so journeys are rhythmic, short, and visually clear
export const CLASS_WORLDS = {
  1: { id: 1, name: "Taj Gardens", icon: "🏛️", sky: 0xdff0fc, pos: [0, 0, -160], subjects: ["maths", "rhymes", "english"] },
  2: { id: 2, name: "Red Fort", icon: "🏰", sky: 0xfce8dc, pos: [140, 0, -80], subjects: ["maths", "hindi", "evs_p2"] },
  3: { id: 3, name: "Qutub Minar", icon: "🗼", sky: 0xfdecd8, pos: [140, 0, 80], subjects: ["maths", "bangla", "evs_p3"] },
  4: { id: 4, name: "Gateway Shore", icon: "⚓", sky: 0xdaf0f3, pos: [0, 0, 160], subjects: ["maths", "evs_p4", "india_map"] },
  5: { id: 5, name: "Victoria Green", icon: "🏛️", sky: 0xe0f4e4, pos: [-140, 0, 80], subjects: ["maths", "evs_p5", "world"] },
  6: { id: 6, name: "Hawa Mahal", icon: "🪟", sky: 0xfce4ec, pos: [-140, 0, -80], subjects: ["maths", "science_p6", "social_p6"] },
  7: { id: 7, name: "Meenakshi Gopuram", icon: "🛕", sky: 0xe8e4f8, pos: [0, 0, -260], subjects: ["maths", "science_p7", "social_p7"] }
};

// Rock-solid stationary ground with a checkered cartoon grass grid
export function buildStaticGround(scene) {
  const size = 3000;
  const canvas = document.createElement('canvas');
  canvas.width = 128;
  canvas.height = 128;
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#6fbc55';
  ctx.fillRect(0, 0, 128, 128);
  ctx.fillStyle = '#63ac4a';
  ctx.fillRect(0, 0, 64, 64);
  ctx.fillRect(64, 64, 64, 64);

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(80, 80);

  const geo = new THREE.PlaneGeometry(size, size);
  const mat = new THREE.MeshStandardMaterial({ map: texture, roughness: 0.9 });
  const ground = new THREE.Mesh(geo, mat);
  ground.rotation.x = -Math.PI / 2;
  ground.position.set(0, -0.01, 0); // Anchored below feet
  ground.matrixAutoUpdate = false;
  ground.updateMatrix();
  scene.add(ground);
  return ground;
}

// Procedural 3D Landmarks
export function build3DLandmark(scene, classId) {
  const world = CLASS_WORLDS[classId];
  const group = new THREE.Group();
  group.position.set(...world.pos);

  if (classId === 1) { // Taj Gardens
    const domeMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });
    const dome = new THREE.Mesh(new THREE.SphereGeometry(14, 24, 16, 0, Math.PI * 2, 0, Math.PI / 2), domeMat);
    dome.position.y = 15;
    const base = new THREE.Mesh(new THREE.BoxGeometry(28, 15, 28), domeMat);
    base.position.y = 7.5;
    group.add(dome, base);
    [[-18,-18], [18,-18], [-18,18], [18,18]].forEach(([mx, mz]) => {
      const p = new THREE.Mesh(new THREE.CylinderGeometry(1.5, 1.8, 30, 12), domeMat);
      p.position.set(mx, 15, mz);
      group.add(p);
    });
  } else if (classId === 2) { // Red Fort
    const fortMat = new THREE.MeshStandardMaterial({ color: 0xb53a3a, roughness: 0.7 });
    const wall = new THREE.Mesh(new THREE.BoxGeometry(45, 18, 14), fortMat);
    wall.position.y = 9;
    const tL = new THREE.Mesh(new THREE.ConeGeometry(7, 10, 8), fortMat);
    tL.position.set(-22, 22, 0);
    const tR = tL.clone();
    tR.position.set(22, 22, 0);
    group.add(wall, tL, tR);
  } else if (classId === 3) { // Qutub Minar
    const mat = new THREE.MeshStandardMaterial({ color: 0xc86432 });
    const tower = new THREE.Mesh(new THREE.CylinderGeometry(3.5, 8, 55, 16), mat);
    tower.position.y = 27.5;
    group.add(tower);
  } else if (classId === 4) { // Gateway of India
    const mat = new THREE.MeshStandardMaterial({ color: 0x8a9597 });
    const p1 = new THREE.Mesh(new THREE.BoxGeometry(8, 28, 10), mat);
    p1.position.set(-11, 14, 0);
    const p2 = p1.clone();
    p2.position.set(11, 14, 0);
    const arch = new THREE.Mesh(new THREE.BoxGeometry(32, 8, 12), mat);
    arch.position.y = 30;
    group.add(p1, p2, arch);
  } else if (classId === 5) { // Victoria Memorial
    const mat = new THREE.MeshStandardMaterial({ color: 0xf5f5f5, roughness: 0.3 });
    const base = new THREE.Mesh(new THREE.BoxGeometry(38, 14, 24), mat);
    base.position.y = 7;
    const dome = new THREE.Mesh(new THREE.SphereGeometry(9, 20, 16, 0, Math.PI*2, 0, Math.PI/2), new THREE.MeshStandardMaterial({ color: 0x3e5f61 }));
    dome.position.y = 14;
    group.add(base, dome);
  } else if (classId === 6) { // Hawa Mahal
    const mat = new THREE.MeshStandardMaterial({ color: 0xef7a67 });
    for (let i = 0; i < 4; i++) {
      const tier = new THREE.Mesh(new THREE.BoxGeometry(36 - i * 7, 7, 6), mat);
      tier.position.set(0, 3.5 + i * 7, 0);
      group.add(tier);
    }
  } else if (classId === 7) { // Meenakshi Temple
    const mat = new THREE.MeshStandardMaterial({ color: 0xe67e22 });
    for (let l = 0; l < 5; l++) {
      const lvl = new THREE.Mesh(new THREE.BoxGeometry(28 - l * 4.5, 6.5, 20 - l * 3), mat);
      lvl.position.set(0, 3.25 + l * 6.5, 0);
      group.add(lvl);
    }
  }

  scene.add(group);
  return group;
}
