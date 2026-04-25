import { Answer, Question, QuestionWithAnswer } from '@/types/types'
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
			const [questionsRes, answersRes] = await Promise.all([
				api.get<Question[]>(`/questions/${projectId}`),
				api.get<Answer[]>(`/answers/${projectId}`),
			])
			const answersByQuestionId = Object.fromEntries(
				answersRes.data.map((a) => [a.questionId, a]),
			)
			questionsByProjectId.value[projectId] = questionsRes.data.map((q) => ({
				...q,
				answer: answersByQuestionId[q.id] ?? null,
			}))
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

	function setQuestions(projectId: number, questions: Question[]): void {
		questionsByProjectId.value[projectId] = questions.map((q) => ({ ...q, answer: null }))
	}

	async function saveAdditionalInfo(
		projectId: number,
		answer: string,
	): Promise<{ success: boolean }> {
		try {
			await api.post(`/projects/${projectId}/additional_info`, { answer })
			return { success: true }
		} catch (error) {
			return { success: false }
		}
	}

	async function generateFollowUpQuestions(
		projectId: number,
	): Promise<{ success: boolean; needsMoreQuestions?: boolean }> {
		loading.value = true
		errorState.value = ''
		try {
			const response = await api.post<{ needsMoreQuestions: boolean; questions: Question[] }>(
				`/questions/${projectId}/follow_up`,
			)
			const { needsMoreQuestions, questions } = response.data
			if (needsMoreQuestions && questions.length) {
				await loadQuestions(projectId)
			}
			return { success: true, needsMoreQuestions }
		} catch (error) {
			errorState.value = getErrorMessage(error, 'Failed to generate follow-up questions')
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
		setQuestions,
		saveAdditionalInfo,
		generateFollowUpQuestions,
	}
})
