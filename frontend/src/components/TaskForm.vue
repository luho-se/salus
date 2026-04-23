<script setup lang="ts">
import { ref } from "vue";
import { useTasksStore } from "../stores/tasks.store";

const tasksStore = useTasksStore();
const title = ref("");
const description = ref("");

const onSubmit = async () => {
	if (!title.value.trim()) {
		return;
	}

	await tasksStore.createTask({
		title: title.value,
		description: description.value
	});

	title.value = "";
	description.value = "";
};
</script>

<template>
	<form class="task-form" @submit.prevent="onSubmit">
		<input v-model="title" type="text" placeholder="Task title" />
		<input v-model="description" type="text" placeholder="Description (optional)" />
		<button type="submit">Add task</button>
	</form>
</template>

<style scoped>
.task-form {
	display: grid;
	gap: 0.75rem;
	grid-template-columns: 2fr 3fr auto;
}

input,
button {
	padding: 0.65rem;
	border-radius: 0.5rem;
	border: 1px solid #d1d5db;
}

button {
	cursor: pointer;
}
</style>
