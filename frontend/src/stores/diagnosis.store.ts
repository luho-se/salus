import { Diagnosis } from '@/types/types'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import api, { getErrorMessage } from '../services/api.service'

export const useDiagnosisStore = defineStore('diagnosis', () => {
	// State
	const diagnosisByProjectId = ref<Record<number, Diagnosis>>({})
	const loading = ref(false)
	const errorState = ref('')

	// Getters
	const getDiagnosisByProjectId = computed(() => {
		return (projectId: number) => diagnosisByProjectId.value[projectId] ?? null
	})

	// Actions
	async function loadDiagnosis(projectId: number): Promise<{ success: boolean }> {
		loading.value = true
		errorState.value = ''

		try {
			const response = await api.get<Diagnosis>(`/projects/${projectId}/diagnosis`)
			diagnosisByProjectId.value[projectId] = response.data
		} catch (error) {
			errorState.value = getErrorMessage(error, 'Failed to load diagnosis')
			return { success: false }
		} finally {
			loading.value = false
			return { success: true }
		}
	}

	async function createDiagnosis(projectId: number): Promise<{ success: boolean }> {
		loading.value = true
		errorState.value = ''

		try {
			const response = await api.post<Diagnosis>(`/projects/${projectId}/diagnosis`)
			diagnosisByProjectId.value[projectId] = response.data
		} catch (error) {
			errorState.value = getErrorMessage(error, 'Failed to create diagnosis')
			return { success: false }
		} finally {
			loading.value = false
			return { success: true }
		}
	}

	return {
		getDiagnosisByProjectId,
		loading,
		errorState,
		loadDiagnosis,
		createDiagnosis,
	}
})
