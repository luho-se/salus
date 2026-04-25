<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { useDiagnosisStore } from '@/stores/diagnosis.store'
import { useQuestionStore } from '@/stores/questions.store'
import { QuestionWithAnswer } from '@/types/types'
import { Pencil, Check, X } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
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

const generatingFollowUp = ref(false)

const latestDiagnosis = computed(() => {
	const list = diagnosisStore.getDiagnosisListByProjectId(projectId)
	return list.length > 0 ? list[0] : null
})

const canStartDiagnosis = computed(() => {
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
	router.push(`/project/${projectId}/questions`)
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
	router.push(`/project/${projectId}/diagnosis/${result.diagnosisId}`)
}
</script>

<template>
	<div class="flex flex-col gap-6 grow p-10 max-w-3xl mx-auto w-full">
		<!-- Header -->
		<div class="flex items-center justify-between">
			<h1 class="text-3xl font-semibold text-secondary-foreground">Your answers</h1>
			<Button variant="outline" class="hover:cursor-pointer"
				@click="router.push(`/project/${projectId}/questions?edit=true`)">
				Edit all
			</Button>
		</div>

		<!-- Loading -->
		<template v-if="questionStore.loading && !questions.length">
			<p class="text-muted-foreground">Loading...</p>
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

			<!-- Actions -->
			<div class="flex justify-between items-center pt-2">
				<TooltipProvider>
					<Tooltip>
						<TooltipTrigger as-child>
							<Button variant="outline" :disabled="generatingFollowUp" class="hover:cursor-pointer" @click="handleGenerateFollowUp">
								<template v-if="generatingFollowUp">
									<div class="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent mr-2" />
									Generating…
								</template>
								<template v-else>
									Generate follow-up questions
								</template>
							</Button>
						</TooltipTrigger>
						<TooltipContent class="max-w-64 text-center">
							More questions typically improve diagnosis accuracy, but each additional question increases computation time.
						</TooltipContent>
					</Tooltip>
				</TooltipProvider>
				<Button :disabled="!canStartDiagnosis || diagnosisStore.loading" class="hover:cursor-pointer" @click="handleStartDiagnosis">
					Start Diagnosis
				</Button>
			</div>
		</template>
	</div>
</template>
