<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useDiagnosisStore } from '@/stores/diagnosis.store'
import { useQuestionStore } from '@/stores/questions.store'
import { QuestionWithAnswer } from '@/types/types'
import { Pencil, Check, X, AlertCircle } from 'lucide-vue-next'
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'

const route = useRoute()
const router = useRouter()
const questionStore = useQuestionStore()
const diagnosisStore = useDiagnosisStore()

const projectId = Number(route.params.id)

const allQuestions = computed(() => questionStore.getQuestionsByProjectId(projectId))
const questions = computed(() =>
	allQuestions.value.filter((q) => q.question !== 'Additional information'),
)
const additionalInfoQuestion = computed(() =>
	allQuestions.value.find((q) => q.question === 'Additional information'),
)

const additionalInfo = ref('')
const editingId = ref<number | null>(null)
const editValue = ref('')

const diagnosisStatus = ref<'IDLE' | 'IN_PROGRESS' | 'FINISHED' | 'FAILED'>('IDLE')
const diagnosisId = ref<number | null>(null)
let pollInterval: ReturnType<typeof setInterval> | null = null

const followUpRecommended = ref<boolean | null>(null)
const generatingFollowUp = ref(false)

const latestDiagnosis = computed(() => {
	const list = diagnosisStore.getDiagnosisListByProjectId(projectId)
	return list.length > 0 ? list[0] : null
})

const canStartDiagnosis = computed(() => {
	if (diagnosisStatus.value === 'IN_PROGRESS') return false
	const answeredQs = allQuestions.value.filter((q) => q.answer?.answer != null)
	if (answeredQs.length === 0) return false
	if (!latestDiagnosis.value) return true
	const lastDiagAt = new Date(latestDiagnosis.value.createdAt).getTime()
	return answeredQs.some((q) => new Date(q.answer!.updatedAt).getTime() > lastDiagAt)
})

onMounted(async () => {
	await Promise.all([
		questionStore.loadQuestions(projectId),
		diagnosisStore.fetchDiagnosisList(projectId),
	])
	if (additionalInfoQuestion.value?.answer?.answer) {
		additionalInfo.value = additionalInfoQuestion.value.answer.answer
	}
})

onUnmounted(() => {
	if (pollInterval) clearInterval(pollInterval)
})

function startEdit(q: QuestionWithAnswer) {
	editingId.value = q.id
	editValue.value = q.answer?.answer ?? ''
}

function cancelEdit() {
	editingId.value = null
	editValue.value = ''
}

async function saveEdit(q: QuestionWithAnswer) {
	const result = await questionStore.submitAnswers(projectId, [
		{ questionId: q.id, answer: editValue.value },
	])
	if (!result.success) {
		toast.error('Failed to save answer')
		return
	}
	editingId.value = null
}

async function handleGenerateFollowUp() {
	generatingFollowUp.value = true
	const result = await questionStore.generateFollowUpQuestions(projectId)
	generatingFollowUp.value = false
	if (!result.success) {
		toast.error(questionStore.errorState || 'Failed to generate follow-up questions')
		return
	}
	followUpRecommended.value = result.needsMoreQuestions ?? false
}

async function handleStartDiagnosis() {
	if (additionalInfo.value.trim()) {
		await questionStore.saveAdditionalInfo(projectId, additionalInfo.value.trim())
	}

	const result = await diagnosisStore.startDiagnosis(projectId)
	if (!result.success) {
		toast.error(diagnosisStore.errorState || 'Failed to start diagnosis')
		return
	}

	diagnosisId.value = result.diagnosisId!
	diagnosisStatus.value = 'IN_PROGRESS'

	pollInterval = setInterval(async () => {
		try {
			const status = await diagnosisStore.pollDiagnosisStatus(diagnosisId.value!)
			diagnosisStatus.value = status
			if (status === 'FINISHED') {
				clearInterval(pollInterval!)
				await diagnosisStore.fetchDiagnosisList(projectId)
				router.push(`/project/${projectId}/diagnosis/${diagnosisId.value}`)
			} else if (status === 'FAILED') {
				clearInterval(pollInterval!)
				diagnosisStatus.value = 'FAILED'
				toast.error('Diagnosis failed. Please try again.')
			}
		} catch (e) {
			clearInterval(pollInterval!)
			diagnosisStatus.value = 'FAILED'
			toast.error('Lost contact with the diagnosis service. Please try again.')
		}
	}, 3000)
}
</script>

<template>
	<div class="flex flex-col gap-6 grow p-10 max-w-3xl mx-auto w-full">
		<!-- Header -->
		<div class="flex items-center justify-between">
			<h1 class="text-3xl font-semibold text-secondary-foreground">Your answers</h1>
			<Button variant="outline" class="hover:cursor-pointer"
				@click="router.push(`/project/${projectId}/questions`)">
				Edit all
			</Button>
		</div>

		<!-- Loading -->
		<template v-if="questionStore.loading && !questions.length">
			<p class="text-muted-foreground">Loading...</p>
		</template>

		<!-- Diagnosis in progress -->
		<template v-else-if="diagnosisStatus === 'IN_PROGRESS'">
			<div class="flex flex-col items-center justify-center py-20 gap-4 text-muted-foreground">
				<div class="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
				<p>Running diagnosis — this may take a moment…</p>
			</div>
		</template>

		<template v-else>
			<!-- Q&A list -->
			<div class="flex flex-col gap-3 overflow-y-auto">
				<Card v-for="q in questions" :key="q.id">
					<CardHeader class="pb-2">
						<div class="flex items-start justify-between gap-4">
							<CardTitle class="text-sm font-medium text-muted-foreground">{{ q.question }}</CardTitle>
							<button v-if="editingId !== q.id"
								class="shrink-0 text-muted-foreground hover:text-foreground transition-colors"
								@click="startEdit(q)">
								<Pencil class="w-4 h-4" />
							</button>
						</div>
					</CardHeader>
					<CardContent>
						<!-- View mode -->
						<template v-if="editingId !== q.id">
							<p class="text-sm">{{ q.answer?.answer ?? '—' }}</p>
						</template>
						<!-- Edit mode -->
						<template v-else>
							<div class="flex flex-col gap-2">
								<textarea v-model="editValue" rows="2"
									class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring resize-none" />
								<div class="flex gap-2 justify-end">
									<button class="text-muted-foreground hover:text-foreground" @click="cancelEdit">
										<X class="w-4 h-4" />
									</button>
									<button class="text-primary hover:opacity-80" @click="saveEdit(q)">
										<Check class="w-4 h-4" />
									</button>
								</div>
							</div>
						</template>
					</CardContent>
				</Card>

				<!-- Additional information -->
				<Card>
					<CardHeader class="pb-2">
						<CardTitle class="text-sm font-medium text-muted-foreground">
							Additional information
							<span class="ml-1 font-normal">(optional)</span>
						</CardTitle>
					</CardHeader>
					<CardContent>
						<textarea v-model="additionalInfo" rows="4"
							placeholder="Any other context that might be relevant..."
							class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring resize-none" />
					</CardContent>
				</Card>
			</div>

			<!-- Follow-up recommendation banner -->
			<div v-if="followUpRecommended === true"
				class="flex items-start justify-between gap-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-200">
				<div class="flex items-start gap-3">
					<AlertCircle class="mt-0.5 h-4 w-4 shrink-0" />
					<p>The AI recommends answering more targeted questions to improve diagnosis accuracy. Follow-up questions have been added.</p>
				</div>
				<button class="shrink-0 underline underline-offset-2 hover:opacity-75 whitespace-nowrap"
					@click="router.push(`/project/${projectId}/questions`)">
					Go to questions
				</button>
			</div>
			<div v-else-if="followUpRecommended === false"
				class="flex items-start gap-3 rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-800 dark:border-green-800 dark:bg-green-950 dark:text-green-200">
				<Check class="mt-0.5 h-4 w-4 shrink-0" />
				<p>The AI determined that your current answers are sufficient for a reliable diagnosis.</p>
			</div>

			<!-- Actions -->
			<div class="flex justify-between items-center pt-2">
				<Button variant="outline" :disabled="generatingFollowUp || diagnosisStatus === 'IN_PROGRESS'" class="hover:cursor-pointer" @click="handleGenerateFollowUp">
					<template v-if="generatingFollowUp">
						<div class="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent mr-2" />
						Checking…
					</template>
					<template v-else>
						Generate follow-up questions
					</template>
				</Button>
				<Button :disabled="!canStartDiagnosis || diagnosisStore.loading" class="hover:cursor-pointer" @click="handleStartDiagnosis">
					Start Diagnosis
				</Button>
			</div>
		</template>
	</div>
</template>
