import { Project } from '@/types/types'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import api, { getErrorMessage } from "../services/api.service";

export const useProjectStore = defineStore('project', () => {
	// State
	const projectsById = ref<Record<number, Project>>({})
	const loading = ref(false)
	const errorState = ref("")

	// Getters
	const projects = computed(() => Object.values(projectsById.value))

	const getProjectById = computed(() => {
		return (projectId: number) => projectsById.value[projectId]
	})

	// Actions
	async function loadProjects(): Promise<{ success: boolean }> {
		loading.value = true;
		errorState.value = "";

		try {
			const response = await api.get<Project[]>("/projects");
			projectsById.value = Object.fromEntries(
				response.data.map((i) => [i.id, i]),
			)
			return {success: true}
		} catch (error) {
			errorState.value = getErrorMessage(error, "Failed to load projects");
			return {success: false}
		} finally {
			loading.value = false;
		}
	}

	async function loadProject(
		projectId: number,
	): Promise<{ success: boolean }> {
		loading.value = true;
		errorState.value = "";

		try {
			const response = await api.get<Project>(`/projects/${projectId}`);
			projectsById.value[projectId] = response.data
			return {success: true}
		} catch (error) {
			errorState.value = getErrorMessage(error, "Failed to load project");
			return {success: false}
		} finally {
			loading.value = false;
		}
	}

	async function submitInitialPrompt(
		projectId: number,
		prompt: string,
	): Promise<{ success: boolean }> {
		loading.value = true;
		errorState.value = "";

		try {
			await api.post(`/projects/${projectId}/generate_questions`, { text: prompt })
			await loadProject(projectId)
			return {success: true}
		} catch (error) {
			errorState.value = getErrorMessage(error, "Failed to submit prompt");
			return {success: false}
		} finally {
			loading.value = false;
		}
	}

	async function createProject(
		payload: {title: string},
	): Promise<{ success: boolean; project?: Project }> {
		loading.value = true;
		errorState.value = "";

		try {
			const response = await api.post<Project>('/projects', payload)
			projectsById.value[response.data.id] = response.data
			return {success: true, project: response.data};
		} catch (error) {
			errorState.value = getErrorMessage(error, "Failed to create project");
			return {success: false}
		} finally {
			loading.value = false;
		}
	}

	return {
		projects,
		getProjectById,
		loading,
		errorState,
		loadProjects,
		loadProject,
		createProject,
		submitInitialPrompt,
	}
})
