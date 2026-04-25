import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import "./main.css";
import "./custom.css"
import router from "./router";

const app = createApp(App);

app.use(router)
app.use(createPinia());
app.mount("#app");
