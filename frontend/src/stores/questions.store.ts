import { QuestionWithAnswer } from '@/types/types'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import api, { getErrorMessage } from '../services/api.service'

export const useQuestionStore = defineStore('question', () => {
	// State
	const questionsByProjectId = ref<Record<number, QuestionWithAnswer[]>>({})
	const loading = ref(false)
	const errorState = ref('')

	// Getters
	const getQuestionsByProjectId = computed(() => {
		return (projectId: number) => questionsByProjectId.value[projectId] ?? []
	})

	// Actions
	async function loadQuestions(projectId: number): Promise<{ success: boolean }> {
		loading.value = true
		errorState.value = ''

		try {
			const response = await api.get<QuestionWithAnswer[]>(`/questions/${projectId}`)
			questionsByProjectId.value[projectId] = response.data
			return { success: true }
		} catch (error) {
			errorState.value = getErrorMessage(error, 'Failed to load questions')
			return { success: false }
		} finally {
			loading.value = false
		}
	}

	async function submitAnswers(
		projectId: number,
		answers: { questionId: number; answer: string }[],
	): Promise<{ success: boolean }> {
		loading.value = true
		errorState.value = ''
		// @todo use generate questions endpoint
		try {
			await api.post(`/answers/${projectId}`, { answers })
			// Re-fetch to get updated answer state
			await loadQuestions(projectId)
			return { success: true }
		} catch (error) {
			errorState.value = getErrorMessage(error, 'Failed to submit answers')
			return { success: false }
		} finally {
			loading.value = false
		}
	}

	return {
		getQuestionsByProjectId,
		loading,
		errorState,
		loadQuestions,
		submitAnswers,
	}
})
