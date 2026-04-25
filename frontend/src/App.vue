<script setup lang="ts">
import { onMounted } from "vue";
import { Toaster } from "vue-sonner";
import { RouterView } from 'vue-router';

document.documentElement.classList.toggle(
	"dark",
	localStorage.theme === "dark" ||
	(!("theme" in localStorage) && window.matchMedia("(prefers-color-scheme: dark)").matches),
);
// Whenever the user explicitly chooses light mode
localStorage.theme = "light";
// Whenever the user explicitly chooses dark mode
localStorage.theme = "dark";
// Whenever the user explicitly chooses to respect the OS preference
localStorage.removeItem("theme");

</script>

<template>
	<Toaster />
	<RouterView class="h-full" />
</template>
