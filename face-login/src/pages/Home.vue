<template>
  <div class="home-page">
    <section class="hero">
      <h1>Welcome to Face Login System</h1>
      <p>Securely log in using facial recognition technology. Get started by registering your face or recognizing a registered user.</p>
      <div class="buttons">
        <router-link to="/register" class="btn">Register Face</router-link>
        <router-link to="/recognize" class="btn btn-primary">Recognize Face</router-link>
      </div>
    </section>

    <section class="features">
      <div class="feature">
        <h2><router-link to="/register" class="btn">Register</router-link></h2>
        <p>Quickly add your face to the system. You only need a few seconds to get started!</p>
      </div>
      <div class="feature">
        <h2><router-link to="/recognize" class="btn btn-primary">Recognize</router-link></h2>
        <p>Verify identities in real-time with the recognition system.</p>
      </div>
    </section>
  </div>
</template>
