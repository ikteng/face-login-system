<template>
  <nav class="navbar">
    <RouterLink to="/" class="nav-item">Home</RouterLink>
    <RouterLink to="/register" class="nav-item">Register User</RouterLink>
    <RouterLink to="/recognize" class="nav-item">Recognize User</RouterLink>

  </nav>
</template>

<script setup>
import { RouterLink } from "vue-router";
import './Navbar.css'
</script>

