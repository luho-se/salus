import { defineStore } from "pinia";
import api, { getErrorMessage } from "../services/api.service";
import type { CreateTaskInput, Task } from "../types/task.types";
import { AxiosError } from "axios";

export const useTasksStore = defineStore("tasks", {
	state: () => ({
		tasks: [] as Task[],
		loading: false,
		error: "" as string,
	}),
	actions: {
		async fetchTasks() {
			this.loading = true;
			this.error = "";

			try {
				const response = await api.get<Task[]>("/tasks");
				this.tasks = response.data;
			} catch (error) {
				this.error = getErrorMessage(error, "Failed to load tasks");
			} finally {
				this.loading = false;
			}
		},

		async createTask(payload: CreateTaskInput) {
			this.error = "";
			try {
				const response = await api.post<Task>("/tasks", payload);
				this.tasks = [response.data, ...this.tasks];
			} catch (error) {
				this.error = getErrorMessage(error, "Failed to create task");
				throw error;
			}
		},

		async toggleTask(task: Task) {
			this.error = "";
			try {
				const response = await api.patch<Task>(`/tasks/${task.id}`, {
					title: task.title,
					description: task.description,
					done: !task.done,
				});
				this.tasks = this.tasks.map((item) =>
					item.id === response.data.id ? response.data : item,
				);
			} catch (error) {
				this.error = getErrorMessage(error, "Failed to update task");
				throw error;
			}
		},

		async deleteTask(taskId: number) {
			this.error = "";
			try {
				await api.delete(`/tasks/${taskId}`);
				this.tasks = this.tasks.filter((task) => task.id !== taskId);
			} catch (error) {
				this.error = getErrorMessage(error, "Failed to delete task");
				throw error;
			}
		},
	},
});
