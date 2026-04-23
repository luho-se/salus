<script setup lang="ts">
import type { Task } from "../types/task.types";
import { useTasksStore } from "../stores/tasks.store";

defineProps<{
	tasks: Task[];
}>();

const tasksStore = useTasksStore();
</script>

<template>
	<ul class="task-list">
		<li v-for="task in tasks" :key="task.id" class="task-item">
			<label>
				<input type="checkbox" :checked="task.done" @change="tasksStore.toggleTask(task)" />
				<span :class="{ done: task.done }">{{ task.title }}</span>
			</label>

			<p v-if="task.description" class="description">{{ task.description }}</p>
			<button class="delete" @click="tasksStore.deleteTask(task.id)">Delete</button>
		</li>
	</ul>
</template>

<style scoped>
.task-list {
	list-style: none;
	padding: 0;
	margin: 0;
	display: grid;
	gap: 0.75rem;
}

.task-item {
	border: 1px solid #d1d5db;
	border-radius: 0.5rem;
	padding: 0.75rem;
}

.description {
	margin: 0.5rem 0;
	color: #6b7280;
}

.done {
	text-decoration: line-through;
}

.delete {
	padding: 0.45rem 0.65rem;
	border-radius: 0.5rem;
	border: 1px solid #ef4444;
	background: white;
	color: #ef4444;
	cursor: pointer;
}
</style>
