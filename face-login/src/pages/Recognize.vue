<template>
  <div class="recognize-container">
    <h2>Real-Time User Recognition</h2>

    <div class="video-wrap" style="position: relative;">
      <video ref="video" autoplay muted></video>
      <canvas ref="overlay" style="position: absolute; top: 0; left: 0;"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import './Recognize.css';

const video = ref(null);
const overlay = ref(null);
let stream = null;
let animationFrameId = null;

onMounted(async () => {
  stream = await navigator.mediaDevices.getUserMedia({ video: true });
  video.value.srcObject = stream;

  // Wait for video to be ready
  await new Promise(r => setTimeout(r, 500));

  overlay.value.width = video.value.videoWidth;
  overlay.value.height = video.value.videoHeight;

  runRecognition();
});

onBeforeUnmount(() => {
  cancelAnimationFrame(animationFrameId);
  if (stream) stream.getTracks().forEach(track => track.stop());
});

async function runRecognition() {
  const canvas = document.createElement("canvas");
  const ctx = canvas.getContext("2d");

  const overlayCtx = overlay.value.getContext("2d");
  canvas.width = video.value.videoWidth;
  canvas.height = video.value.videoHeight;
  overlay.value.width = video.value.videoWidth;
  overlay.value.height = video.value.videoHeight;

  async function loop() {
    if (video.value.videoWidth === 0 || video.value.videoHeight === 0) {
      animationFrameId = requestAnimationFrame(loop);
      return;
    }

    ctx.drawImage(video.value, 0, 0, canvas.width, canvas.height);
    const imgData = canvas.toDataURL("image/jpeg");

    try {
      const res = await fetch("http://localhost:8000/recognize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: "-", image: imgData }),
      });

      const result = await res.json();

      overlayCtx.clearRect(0, 0, overlay.value.width, overlay.value.height);

      if (result && result.face_box) {
        const box = result.face_box;
        overlayCtx.strokeStyle = "#00FF00";
        overlayCtx.lineWidth = 2;
        overlayCtx.strokeRect(box.x, box.y, box.width, box.height);

        overlayCtx.fillStyle = "#00FF00";
        overlayCtx.font = "20px Arial";
        overlayCtx.fillText(`${result.name} (${result.score.toFixed(2)})`, box.x, box.y - 10);
      }
    } catch (err) {
      console.error("Recognition error:", err);
    }

    animationFrameId = requestAnimationFrame(loop);
  }

  loop();
}
</script>

