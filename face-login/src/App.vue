<template>
  <div>
    <Navbar />
    <main class="main-container">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { RouterView } from "vue-router";
import Navbar from "./components/Navbar.vue";
</script>

<style>
.main-container {
  padding: 20px;
}
</style>
