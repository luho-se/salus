<script setup lang="ts">
import { onMounted } from "vue";
import TaskForm from "./components/TaskForm.vue";
import TaskList from "./components/TaskList.vue";
import { useTasksStore } from "./stores/tasks.store";

const tasksStore = useTasksStore();

onMounted(() => {
	tasksStore.fetchTasks();
});
</script>

<template>
	<main class="container">
		<h1>Hackathon Template: Tasks</h1>
		<p class="subtitle">Flask + PostgreSQL + Vue + Pinia</p>
		<TaskForm />

		<p v-if="tasksStore.loading">Loading tasks...</p>
		<p v-if="tasksStore.error" class="error">{{ tasksStore.error }}</p>
		<TaskList :tasks="tasksStore.tasks" />
	</main>
</template>

<style scoped>
.container {
	max-width: 800px;
	margin: 2rem auto;
	padding: 0 1rem;
	display: grid;
	gap: 1rem;
	font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.subtitle {
	margin-top: -0.5rem;
	color: #6b7280;
}

.error {
	color: #ef4444;
}
</style>
