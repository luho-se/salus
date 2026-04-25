import { Diagnosis, DiagnosisItem } from '@/types/types'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import api, { getErrorMessage } from '../services/api.service'

export const useDiagnosisStore = defineStore('diagnosis', () => {
	// State
	const diagnosisByProjectId = ref<Record<number, Diagnosis>>({})
	const diagnosisIdByProjectId = ref<Record<number, number>>({})
	const loading = ref(false)
	const errorState = ref('')

	// Getters
	const getDiagnosisByProjectId = computed(() => {
		return (projectId: number) => diagnosisByProjectId.value[projectId] ?? null
	})

	// Actions
	async function createDiagnosis(projectId: number): Promise<{ success: boolean }> {
		loading.value = true
		errorState.value = ''

		try {
			const createResponse = await api.post<{ diagnosisId: number }>(`/diagnosis/${projectId}`)
			const diagnosisId = createResponse.data.diagnosisId
			diagnosisIdByProjectId.value[projectId] = diagnosisId

			const itemsResponse = await api.get<DiagnosisItem[]>(`/diagnosis/${diagnosisId}/items`)
			diagnosisByProjectId.value[projectId] = {
				id: diagnosisId,
				projectId,
				createdAt: new Date().toISOString(),
				items: itemsResponse.data,
				sentenceWeights: [],
			}
			return { success: true }
		} catch (error) {
			errorState.value = getErrorMessage(error, 'Failed to create diagnosis')
			return { success: false }
		} finally {
			loading.value = false
		}
	}

	async function loadDiagnosis(projectId: number): Promise<{ success: boolean }> {
		const diagnosisId = diagnosisIdByProjectId.value[projectId]
		if (!diagnosisId) return createDiagnosis(projectId)

		loading.value = true
		errorState.value = ''

		try {
			const itemsResponse = await api.get<DiagnosisItem[]>(`/diagnosis/${diagnosisId}`)
			diagnosisByProjectId.value[projectId] = {
				...diagnosisByProjectId.value[projectId],
				items: itemsResponse.data,
			}
			return { success: true }
		} catch (error) {
			errorState.value = getErrorMessage(error, 'Failed to load diagnosis')
			return { success: false }
		} finally {
			loading.value = false
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
