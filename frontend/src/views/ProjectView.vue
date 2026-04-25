<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { useProjectStore } from '@/stores/projects.store'
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'

const route = useRoute()
const router = useRouter()
const projectStore = useProjectStore()

const projectId = Number(route.params.id)
const prompt = ref('')

const project = computed(() => projectStore.getProjectById(projectId))

onMounted(() => projectStore.loadProject(projectId))

async function handleSubmitPrompt() {
	if (!prompt.value.trim()) return
	const result = await projectStore.submitInitialPrompt(projectId, prompt.value.trim())
	if (!result.success) {
		toast.error(projectStore.errorState || 'Failed to submit prompt')
		return
	}
	router.push(`/project/${projectId}/questions`)
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
				<div class="flex flex-col gap-4">
					<p class="text-muted-foreground">Describe your situation in as much detail as you can. We'll use this to generate targeted questions.</p>
					<textarea
						v-model="prompt"
						rows="6"
						placeholder="e.g. I've had a sharp pain in my lower left leg for two weeks, mainly when walking..."
						class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring resize-none"
					/>
					<div class="flex justify-end">
						<Button
							:disabled="!prompt.trim() || projectStore.loading"
							class="hover:cursor-pointer"
							@click="handleSubmitPrompt"
						>
							Analyse
						</Button>
					</div>
				</div>
			</template>

			<!-- INITIAL_QUESTIONS / DIAGNOSIS: read-only prompt + action -->
			<template v-else>
				<Card>
					<CardContent class="pt-6">
						<p class="text-sm text-muted-foreground whitespace-pre-wrap">{{ project.initialPrompt }}</p>
					</CardContent>
				</Card>

				<div class="flex justify-end">
					<Button
						v-if="project.step === 'INITIAL_QUESTIONS'"
						class="hover:cursor-pointer"
						@click="router.push(`/project/${projectId}/questions`)"
					>
						Answer questions
					</Button>
					<Button
						v-else-if="project.step === 'DIAGNOSIS'"
						class="hover:cursor-pointer"
						@click="router.push(`/project/${projectId}/diagnosis`)"
					>
						View diagnosis
					</Button>
				</div>
			</template>
		</template>
	</div>
</template>
