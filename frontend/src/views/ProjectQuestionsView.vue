<script setup lang="ts">
import BodyLocationSelector from '@/components/BodyLocationSelector.vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { useQuestionStore } from '@/stores/questions.store'
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'

const route = useRoute()
const router = useRouter()
const questionStore = useQuestionStore()

const projectId = Number(route.params.id)
const currentIndex = ref(0)
const answers = ref<Record<number, string>>({})

const questions = computed(() => questionStore.getQuestionsByProjectId(projectId))
const currentQuestion = computed(() => questions.value[currentIndex.value])
const isFirst = computed(() => currentIndex.value === 0)
const isLast = computed(() => currentIndex.value === questions.value.length - 1)
const currentAnswer = computed({
	get: () => answers.value[currentQuestion.value?.id] ?? '',
	set: (val) => { answers.value[currentQuestion.value.id] = val },
})

onMounted(async () => {
	await questionStore.loadQuestions(projectId)
	// Pre-populate answers from existing data
	for (const q of questions.value) {
		if (q.answer?.answer != null) {
			answers.value[q.id] = q.answer.answer
		}
	}
})

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
		toast.error(questionStore.errorState || 'Failed to submit answers')
		return
	}
	router.push(`/project/${projectId}`)
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
			<Card class="min-h-64">
				<CardHeader>
					<CardTitle class="text-xl font-medium leading-snug">
						{{ currentQuestion.question }}
					</CardTitle>
				</CardHeader>
				<CardContent>
					<!-- text input -->
					<Input v-if="currentQuestion.inputType === 'text'" v-model="currentAnswer" type="text"
						placeholder="Your answer..." />

					<!-- number input -->
					<div v-else-if="currentQuestion.inputType === 'number'" class="flex items-center gap-2">
						<Input v-model="currentAnswer" type="number" :min="currentQuestion.inputMin ?? undefined"
							:max="currentQuestion.inputMax ?? undefined" placeholder="0" class="max-w-40" />
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
					Submit
				</Button>
			</div>
		</template>

		<template v-else-if="!questionStore.loading">
			<p class="text-muted-foreground">No questions available yet.</p>
		</template>
	</div>
</template>
