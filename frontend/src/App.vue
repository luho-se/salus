<script setup lang="ts">
import { Toaster } from '@/components/ui/sonner'
import 'vue-sonner/style.css'
import { RouterView } from 'vue-router';

document.documentElement.classList.toggle(
	"dark",
	localStorage.theme === "dark" ||
	(!("theme" in localStorage) && window.matchMedia("(prefers-color-scheme: dark)").matches),
);

</script>

<template>
	<Toaster position="bottom-right" rich-colors />
	<RouterView class="h-full" />
</template>
