<template>
  <div class="page">
    <h1>Register New User</h1>
    <div class="register-container">
        <div class="input-row">
            <label class="label">Username:</label>
            <input
                v-model="username"
                class="input"
                placeholder="Enter username"
            />
        </div>

        <div class="grid">
            <div
                v-for="(img, index) in images"
                :key="index"
                class="image-slot"
            >
                <img v-if="img" :src="img" />
                <div v-else class="placeholder">
                <button @click="openCamera(index)">Use Camera</button>
                <p>or</p>
                <input type="file" accept="image/*" @change="handleFileUpload($event, index)" />
                </div>
            </div>
        </div>

        <!-- Popup camera modal -->
        <div v-if="showCamera" class="camera-modal">
        <video ref="video" autoplay></video>

        <div class="camera-buttons">
            <button class="capture-btn" @click="captureImage">
                Capture
            </button>
            <button class="cancel-btn" @click="closeCamera">
                Cancel
            </button>
        </div>
        </div>

        <p v-if="message" class="message">{{ message }}</p>

    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import "./Register.css";

const username = ref("");
const images = ref([null, null, null, null]); // 3 slots
const message = ref("");

const video = ref(null);
const showCamera = ref(false);
let activeIndex = 0; // which slot we are capturing into
let stream = null;

function openCamera(index) {
  if (!username.value) {
    message.value = "Please enter a username first.";
    return;
  }
  activeIndex = index;
  startCamera();
}

async function startCamera() {
  showCamera.value = true;
  stream = await navigator.mediaDevices.getUserMedia({ video: true });
  video.value.srcObject = stream;
}

function closeCamera() {
  showCamera.value = false;
  if (stream) stream.getTracks().forEach((t) => t.stop());
}

async function captureImage() {
  const canvas = document.createElement("canvas");
  canvas.width = video.value.videoWidth;
  canvas.height = video.value.videoHeight;

  const ctx = canvas.getContext("2d");
  ctx.drawImage(video.value, 0, 0);

  const imgData = canvas.toDataURL("image/jpeg");
  images.value[activeIndex] = imgData;

  await sendToServer(imgData);

  closeCamera();
}

// New function to handle file upload
async function handleFileUpload(event, index) {
  if (!username.value) {
    message.value = "Please enter a username first.";
    return;
  }

  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = async (e) => {
    const imgData = e.target.result;
    images.value[index] = imgData;
    activeIndex = index;
    await sendToServer(imgData);
  };
  reader.readAsDataURL(file);
}

async function sendToServer(img) {
  const payload = {
    username: username.value,
    image: img,
  };

  const res = await fetch("http://localhost:8000/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await res.json();
  message.value = data.message;
}
</script>
