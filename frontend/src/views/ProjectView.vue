<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useProjectStore } from '@/stores/projects.store'
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'

const route = useRoute()
const router = useRouter()
const projectStore = useProjectStore()

const projectId = computed(() => Number(route.params.id))
const prompt = ref('')
const generating = ref(false)

const project = computed(() => projectStore.getProjectById(projectId.value))

onMounted(() => projectStore.loadProject(projectId.value))

async function handleSubmitPrompt() {
	const projectIdSnapshot = projectId.value
	if (!prompt.value.trim()) return
	generating.value = true
	const result = await projectStore.submitInitialPrompt(projectIdSnapshot, prompt.value.trim())
	generating.value = false
	if (!result.success) {
		toast.error(projectStore.errorState || 'Failed to submit prompt')
		return
	}
	router.push(`/project/${projectIdSnapshot}/questions`)
}
</script>

<template>
	<div class="flex flex-col gap-8 grow p-10 max-w-3xl mx-auto w-full">
		<template v-if="projectStore.loading && !project">
			<p class="text-muted-foreground">Loading...</p>
		</template>

		<template v-else-if="project">
			<h1 class="text-3xl font-semibold text-secondary-foreground">{{ project.title }}</h1>

			<!-- INITIAL_PROMPT: enter the prompt -->
			<template v-if="project.step === 'INITIAL_PROMPT'">
				<!-- Generating questions spinner -->
				<template v-if="generating">
					<div class="flex flex-col items-center justify-center py-20 gap-4 text-muted-foreground">
						<div class="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
						<p>Analysing your description and generating questions…</p>
					</div>
				</template>

				<template v-else>
					<p class="text-muted-foreground">Describe your situation in as much detail as you can. We'll use
						this to generate targeted questions.</p>
					<textarea v-model="prompt" rows="6"
						placeholder="e.g. I've had a sharp pain in my lower left leg for two weeks, mainly when walking..."
						class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring resize-none" />
					<div class="flex justify-end">
						<Button :disabled="!prompt.trim()" class="hover:cursor-pointer" @click="handleSubmitPrompt">
							Analyse
						</Button>
					</div>
				</template>
			</template>

			<!-- INITIAL_QUESTIONS / DIAGNOSIS: description summary + action -->
			<template v-else>
				<Card>
					<CardHeader>
						<CardTitle class="text-sm font-medium text-muted-foreground uppercase tracking-wide">
							Your description
						</CardTitle>
					</CardHeader>
					<CardContent>
						<p class="text-sm leading-relaxed whitespace-pre-wrap">{{ project.initialPrompt }}</p>
					</CardContent>
				</Card>

				<template v-if="project.step === 'INITIAL_QUESTIONS'">
					<div class="flex flex-col gap-3">
						<p class="text-sm text-muted-foreground">
							Questions have been generated based on your description. Review your answers or start the diagnosis.
						</p>
						<div class="flex justify-end">
							<Button class="hover:cursor-pointer"
								@click="router.push(`/project/${projectId}/summary`)">
								Question summary
							</Button>
						</div>
					</div>
				</template>

				<template v-else-if="project.step === 'DIAGNOSIS'">
					<div class="flex flex-col gap-3">
						<p class="text-sm text-muted-foreground">
							Your diagnosis is ready.
						</p>
						<div class="flex justify-end">
							<Button class="hover:cursor-pointer"
								@click="router.push(`/project/${projectId}/diagnosis`)">
								View diagnosis
							</Button>
						</div>
					</div>
				</template>
			</template>
		</template>
	</div>
</template>
