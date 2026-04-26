<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { useDiagnosisStore } from '@/stores/diagnosis.store'
import { useProjectStore } from '@/stores/projects.store'
import { ChevronRight } from 'lucide-vue-next'
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'

const route = useRoute()
const router = useRouter()
const projectStore = useProjectStore()
const diagnosisStore = useDiagnosisStore()

const projectId = computed(() => Number(route.params.id))
const prompt = ref('')
const generating = ref(false)

const project = computed(() => projectStore.getProjectById(projectId.value))
const diagnosisList = computed(() => diagnosisStore.getDiagnosisListByProjectId(projectId.value))

async function loadData(id: number) {
	await projectStore.loadProject(id)
	if (project.value?.step !== 'INITIAL_PROMPT') {
		diagnosisStore.fetchDiagnosisList(id)
	}
}

onMounted(() => loadData(projectId.value))
watch(projectId, (id) => loadData(id))

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

function formatDiagnosisDate(iso: string): string {
	return new Date(iso).toLocaleString(undefined, {
		month: 'short',
		day: 'numeric',
		year: 'numeric',
		hour: '2-digit',
		minute: '2-digit',
	})
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

			<!-- Post-prompt: description card + actions + diagnosis history -->
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

				<div class="flex justify-end">
					<Button class="hover:cursor-pointer"
						@click="router.push(`/project/${projectId}/summary`)">
						Question summary
					</Button>
				</div>

				<!-- Diagnosis history -->
				<template v-if="diagnosisList.length">
					<Separator />
					<div class="flex flex-col gap-2">
						<p class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
							Previous diagnoses
						</p>
						<div
							v-for="(d, i) in diagnosisList"
							:key="d.id"
							class="flex items-center justify-between px-3 py-2.5 rounded-lg border hover:bg-muted/50 cursor-pointer transition-colors"
							@click="router.push(`/project/${projectId}/diagnosis/${d.id}`)"
						>
							<div class="flex items-center gap-2">
								<span class="text-sm">{{ formatDiagnosisDate(d.createdAt) }}</span>
								<span v-if="i === 0"
									class="text-xs px-1.5 py-0.5 rounded-full bg-primary/10 text-primary font-medium">
									Latest
								</span>
							</div>
							<ChevronRight class="w-4 h-4 text-muted-foreground" />
						</div>
					</div>
				</template>
			</template>
		</template>
	</div>
</template>
