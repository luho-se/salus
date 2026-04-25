<script setup lang="ts">
import BodyLocationSelector from '@/components/BodyLocationSelector.vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { useQuestionStore } from '@/stores/questions.store'
import { computed, onMounted, watch, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'

const route = useRoute()
const router = useRouter()
const questionStore = useQuestionStore()

const projectId = Number(route.params.id)
const editMode = route.query.edit === 'true'
const currentIndex = ref(0)
const answers = ref<Record<number, string>>({})

const allQuestions = computed(() => questionStore.getQuestionsByProjectId(projectId))
const questions = computed(() =>
	allQuestions.value.filter((q) => q.question !== 'Additional information'),
)
const currentQuestion = computed(() => questions.value[currentIndex.value] ?? null)
const isFirst = computed(() => currentIndex.value === 0)
const isLast = computed(() => currentIndex.value === questions.value.length - 1)

const hasMinMax = computed(() =>
	currentQuestion.value?.inputMin !== null &&
	currentQuestion.value?.inputMax !== null &&
	currentQuestion.value?.inputType === 'number',
)

const currentAnswer = computed({
	get: () => (currentQuestion.value ? (answers.value[currentQuestion.value.id] ?? '') : ''),
	set: (val) => {
		if (currentQuestion.value) answers.value[currentQuestion.value.id] = val
	},
})

const sliderDisplayValue = computed(() => {
	const n = parseFloat(currentAnswer.value)
	return isNaN(n) ? (currentQuestion.value?.inputMin ?? 0) : n
})

// Initialize slider to min when navigating to an unanswered number question with min/max
watch(currentQuestion, (q) => {
	if (!q) return
	if (q.inputType === 'number' && q.inputMin !== null && q.inputMax !== null && !answers.value[q.id]) {
		answers.value[q.id] = String(q.inputMin)
	}
})

onMounted(async () => {
	await questionStore.loadQuestions(projectId)
	const allAnswered =
		!editMode &&
		questions.value.length > 0 &&
		questions.value.every((q) => q.answer?.answer != null)
	if (allAnswered) {
		router.replace(`/project/${projectId}/summary`)
		return
	}
	// Pre-fill existing answers
	for (const q of questions.value) {
		if (q.answer?.answer != null) {
			answers.value[q.id] = q.answer.answer
		}
	}
	// Jump to first unanswered (skip in edit mode — start from beginning)
	if (!editMode) {
		const firstUnanswered = questions.value.findIndex((q) => !answers.value[q.id])
		if (firstUnanswered > 0) currentIndex.value = firstUnanswered
	}
})

function clampCurrentAnswer() {
	const q = currentQuestion.value
	if (!q) return
	const val = parseFloat(currentAnswer.value)
	if (isNaN(val)) return
	if (q.inputMin !== null && val < q.inputMin) currentAnswer.value = String(q.inputMin)
	if (q.inputMax !== null && val > q.inputMax) currentAnswer.value = String(q.inputMax)
}

function goNext() {
	if (!isLast.value) currentIndex.value++
}

function goBack() {
	if (!isFirst.value) currentIndex.value--
}

async function handleSubmit() {
	const answersArray = Object.entries(answers.value).map(([questionId, answer]) => ({
		questionId: Number(questionId),
		answer,
	}))
	const result = await questionStore.submitAnswers(projectId, answersArray)
	if (!result.success) {
		toast.error(questionStore.errorState || 'Failed to save answers')
		return
	}
	router.push(`/project/${projectId}/summary`)
}
</script>

<template>
	<div class="flex flex-col gap-8 grow p-10 max-w-3xl mx-auto w-full">
		<template v-if="questionStore.loading && !questions.length">
			<p class="text-muted-foreground">Loading questions...</p>
		</template>

		<template v-else-if="questions.length">
			<!-- Progress -->
			<div class="flex items-center justify-between">
				<span class="text-sm text-muted-foreground">
					Question {{ currentIndex + 1 }} of {{ questions.length }}
				</span>
				<div class="flex gap-1">
					<div v-for="(_, i) in questions" :key="i" class="h-1.5 w-6 rounded-full transition-colors"
						:class="i <= currentIndex ? 'bg-primary' : 'bg-muted'" />
				</div>
			</div>

			<!-- Question card -->
			<Card v-if="currentQuestion" class="min-h-64">
				<CardHeader>
					<CardTitle class="text-xl font-medium leading-snug">
						{{ currentQuestion.question }}
					</CardTitle>
				</CardHeader>
				<CardContent>
					<!-- text input -->
					<Input v-if="currentQuestion.inputType === 'text'" v-model="currentAnswer" type="text"
						placeholder="Your answer..." />

					<!-- number with min+max → slider -->
					<div v-else-if="currentQuestion.inputType === 'number' && hasMinMax" class="flex flex-col gap-4">
						<div class="flex items-baseline justify-center gap-1.5">
							<span class="text-5xl font-semibold tabular-nums">{{ sliderDisplayValue }}</span>
							<span v-if="currentQuestion.inputUnit" class="text-lg text-muted-foreground">
								{{ currentQuestion.inputUnit }}
							</span>
						</div>
						<input
							type="range"
							v-model="currentAnswer"
							:min="currentQuestion.inputMin!"
							:max="currentQuestion.inputMax!"
							step="1"
							class="w-full h-2 rounded-full appearance-none cursor-pointer accent-primary bg-muted"
						/>
						<div class="flex justify-between text-xs text-muted-foreground">
							<span>{{ currentQuestion.inputMin }}{{ currentQuestion.inputUnit ? ' ' + currentQuestion.inputUnit : '' }}</span>
							<span>{{ currentQuestion.inputMax }}{{ currentQuestion.inputUnit ? ' ' + currentQuestion.inputUnit : '' }}</span>
						</div>
					</div>

					<!-- number without min/max → plain input -->
					<div v-else-if="currentQuestion.inputType === 'number'" class="flex items-center gap-2">
						<Input v-model="currentAnswer" type="number"
							:min="currentQuestion.inputMin ?? undefined"
							:max="currentQuestion.inputMax ?? undefined"
							placeholder="0"
							class="max-w-40"
							@change="clampCurrentAnswer"
							@blur="clampCurrentAnswer" />
						<span v-if="currentQuestion.inputUnit" class="text-sm text-muted-foreground">
							{{ currentQuestion.inputUnit }}
						</span>
					</div>

					<!-- body_location selector -->
					<BodyLocationSelector v-else-if="currentQuestion.inputType === 'body_location'"
						v-model="currentAnswer" />
				</CardContent>
			</Card>

			<!-- Navigation -->
			<div class="flex justify-between">
				<Button variant="outline" :disabled="isFirst" class="hover:cursor-pointer" @click="goBack">
					Back
				</Button>

				<Button v-if="!isLast" :disabled="!currentAnswer.toString().trim()" class="hover:cursor-pointer"
					@click="goNext">
					Next
				</Button>
				<Button v-else :disabled="!currentAnswer.toString().trim() || questionStore.loading"
					class="hover:cursor-pointer" @click="handleSubmit">
					Save answers
				</Button>
			</div>
		</template>

		<template v-else-if="!questionStore.loading">
			<p class="text-muted-foreground">No questions available yet.</p>
		</template>
	</div>
</template>
