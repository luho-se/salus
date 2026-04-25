import { Diagnosis, DiagnosisItem, DiagnosisSentenceWeight, SlimDiagnosis } from '@/types/types'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import api, { getErrorMessage } from '../services/api.service'

export const useDiagnosisStore = defineStore('diagnosis', () => {
	// State
	const diagnosisByDiagnosisId = ref<Record<number, Diagnosis>>({})
	const diagnosisListByProjectId = ref<Record<number, SlimDiagnosis[]>>({})
	const loading = ref(false)
	const errorState = ref('')

	// Getters
	const getDiagnosisByDiagnosisId = computed(() => {
		return (diagnosisId: number) => diagnosisByDiagnosisId.value[diagnosisId] ?? null
	})

	const getDiagnosisListByProjectId = computed(() => {
		return (projectId: number) => diagnosisListByProjectId.value[projectId] ?? []
	})

	// Shared response shape from GET /diagnosis/:id
	interface DiagnosisResponse {
		id: number
		projectId: number
		createdAt: string
		diagnosisItems: DiagnosisItem[]
		diagnosisWeights: DiagnosisSentenceWeight[]
	}

	function storeFromResponse(d: DiagnosisResponse): Diagnosis {
		return {
			id: d.id,
			projectId: d.projectId,
			createdAt: d.createdAt,
			items: d.diagnosisItems,
			sentenceWeights: d.diagnosisWeights,
		}
	}

	async function loadDiagnosisByDiagnosisId(diagnosisId: number): Promise<{ success: boolean }> {
		loading.value = true
		errorState.value = ''
		try {
			const response = await api.get<DiagnosisResponse>(`/diagnosis/${diagnosisId}`)
			diagnosisByDiagnosisId.value[diagnosisId] = storeFromResponse(response.data)
			return { success: true }
		} catch (error) {
			errorState.value = getErrorMessage(error, 'Failed to load diagnosis')
			return { success: false }
		} finally {
			loading.value = false
		}
	}

	async function fetchDiagnosisList(projectId: number): Promise<void> {
		try {
			const response = await api.get<{ diagnoses: SlimDiagnosis[] }>(`/diagnosis/list/${projectId}/slim`)
			diagnosisListByProjectId.value[projectId] = response.data.diagnoses
		} catch {
			diagnosisListByProjectId.value[projectId] = []
		}
	}

	async function startDiagnosis(projectId: number): Promise<{ success: boolean; diagnosisId?: number }> {
		loading.value = true
		errorState.value = ''
		try {
			const response = await api.post<{ diagnosisId: number }>(`/diagnosis/${projectId}`)
			const diagnosisId = response.data.diagnosisId
			return { success: true, diagnosisId }
		} catch (error) {
			errorState.value = getErrorMessage(error, 'Failed to start diagnosis')
			return { success: false }
		} finally {
			loading.value = false
		}
	}

	type DiagnosisStatus = 'IN_PROGRESS' | 'FINISHED' | 'FAILED'

	async function pollDiagnosisStatus(diagnosisId: number): Promise<DiagnosisStatus> {
		const response = await api.get<{ status: DiagnosisStatus }>(`/diagnosis/${diagnosisId}/status`)
		return response.data.status
	}

	return {
		getDiagnosisByDiagnosisId,
		getDiagnosisListByProjectId,
		loading,
		errorState,
		loadDiagnosisByDiagnosisId,
		fetchDiagnosisList,
		startDiagnosis,
		pollDiagnosisStatus,
	}
})
