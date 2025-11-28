import { createApp } from "vue";
import "./style.css";
import App from "./App.vue";

import { createRouter, createWebHistory } from "vue-router";

// Pages
import Home from "./pages/Home.vue";
import Register from "./pages/Register.vue";
import Recognize from "./pages/Recognize.vue";

// Define routes
const routes = [
  { path: "/", name: "Home", component: Home },
  { path: "/register", name: "Register", component: Register },
  { path: "/recognize", name: "Recognize", component: Recognize },
];

// Create router
const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Mount app
createApp(App).use(router).mount("#app");
