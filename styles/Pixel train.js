const canvas = document.createElement('canvas');
document.body.appendChild(canvas);
const ctx = canvas.getContext('2d');

canvas.width = window.innerWidth;
canvas.height = 200;
const p = 8; // "Pixel" size
let xPos = -100; // Starting position (off-screen left)

// 0: transparent, 1: red, 2: black (wheels), 3: blue (window), 4: dark red (smoke)
const trainMap = [
  [0,0,0,0,0,0,0,4,4,4,0,0],
  [0,0,0,0,0,0,0,1,1,1,0,0],
  [0,4,0,0,1,1,1,1,3,1,0,0],
  [1,1,1,1,1,1,1,1,1,1,1,1],
  [1,1,1,1,1,1,1,1,1,1,1,1],
  [0,2,2,0,0,2,2,0,0,2,2,0]
];

const colors = ["transparent", "#e63946", "#1d3557", "#a8dadc", "#a01a24"];

function animate() {
  // 1. Clear the canvas to prepare for the next frame
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // 2. Loop through the grid and draw the train at its current xPos
  trainMap.forEach((row, y) => {
    row.forEach((pixel, x) => {
      if (pixel !== 0) {
        ctx.fillStyle = colors[pixel];
        ctx.fillRect(xPos + (x * p), 50 + (y * p), p, p);
      }
    });
  });

  // 3. Move the train position
  xPos += 2; // Change this number to speed up/slow down

  // 4. Loop back to start if it goes off screen
  if (xPos > canvas.width) {
    xPos = -150;
  }

  // 5. Tell the browser to call animate() for the next frame
  requestAnimationFrame(animate);
}

// Start the animation
animate();
