<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useDiagnosisStore } from '@/stores/diagnosis.store'
import { DiagnosisCareType, DiagnosisItemProbability } from '@/types/types'
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'

const route = useRoute()
const router = useRouter()
const diagnosisStore = useDiagnosisStore()

const projectId = Number(route.params.id)
const diagnosisId = Number(route.params.diagnosisId)
const diagnosis = computed(() => diagnosisStore.getDiagnosisByDiagnosisId(diagnosisId))

type JobStatus = 'IN_PROGRESS' | 'FINISHED' | 'FAILED'
const jobStatus = ref<JobStatus | null>(null)
let pollInterval: ReturnType<typeof setInterval> | null = null

onMounted(async () => {
	try {
		const status = await diagnosisStore.pollDiagnosisStatus(diagnosisId)
		jobStatus.value = status
		if (status === 'IN_PROGRESS') {
			startPolling()
		} else {
			await loadDiagnosis()
		}
	} catch {
		// No status record (older diagnosis) — try loading directly
		await loadDiagnosis()
	}
})

onUnmounted(() => {
	if (pollInterval) clearInterval(pollInterval)
})

function startPolling() {
	pollInterval = setInterval(async () => {
		try {
			const status = await diagnosisStore.pollDiagnosisStatus(diagnosisId)
			jobStatus.value = status
			if (status !== 'IN_PROGRESS') {
				clearInterval(pollInterval!)
				if (status === 'FINISHED') await loadDiagnosis()
			}
		} catch {
			clearInterval(pollInterval!)
		}
	}, 3000)
}

async function loadDiagnosis() {
	const result = await diagnosisStore.loadDiagnosisByDiagnosisId(diagnosisId)
	if (!result.success) {
		toast.error(diagnosisStore.errorState || 'Failed to load diagnosis')
	}
}

const probabilityLabel: Record<DiagnosisItemProbability, string> = {
	LOW: 'Low probability',
	MEDIUM: 'Medium probability',
	HIGH: 'High probability',
}

const probabilityStyle: Record<DiagnosisItemProbability, string> = {
	LOW: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
	MEDIUM: 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200',
	HIGH: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
}

const careTypeLabel: Record<DiagnosisCareType, string> = {
	SELF_CARE: 'Self-care',
	PROFESSIONAL_CARE: 'See a professional',
	EMERGENCY_CARE: 'Emergency care',
}

const careTypeStyle: Record<DiagnosisCareType, string> = {
	SELF_CARE: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
	PROFESSIONAL_CARE: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
	EMERGENCY_CARE: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
}
</script>

<template>
	<div class="flex flex-col gap-8 grow p-10 max-w-3xl mx-auto w-full">
		<div class="flex items-center justify-between">
			<h1 class="text-3xl font-semibold text-secondary-foreground">Diagnosis</h1>
			<Button variant="outline" class="hover:cursor-pointer" @click="router.push(`/project/${projectId}`)">
				Back to project
			</Button>
		</div>

		<!-- Job running -->
		<template v-if="jobStatus === 'IN_PROGRESS'">
			<div class="flex flex-col items-center justify-center py-20 gap-4 text-muted-foreground">
				<div class="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
				<p>Generating diagnosis — this may take a moment…</p>
			</div>
		</template>

		<!-- Fetching results from DB -->
		<template v-else-if="diagnosisStore.loading">
			<div class="flex flex-col items-center justify-center py-20 gap-4 text-muted-foreground">
				<div class="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
				<p>Loading diagnosis…</p>
			</div>
		</template>

		<!-- Job failed -->
		<template v-else-if="jobStatus === 'FAILED'">
			<div class="flex flex-col items-center justify-center py-20 gap-4 text-muted-foreground">
				<p class="text-destructive">Diagnosis failed. Please go back and try again.</p>
				<Button variant="outline" @click="router.push(`/project/${projectId}/summary`)">
					Back to summary
				</Button>
			</div>
		</template>

		<!-- Results -->
		<template v-else-if="diagnosis">
			<div class="flex flex-col gap-4">
				<Card v-for="item in diagnosis.items" :key="item.id">
					<CardHeader>
						<div class="flex items-start justify-between gap-4">
							<CardTitle class="text-lg">{{ item.title }}</CardTitle>
							<div class="flex flex-col gap-1 items-end shrink-0">
								<span class="text-xs font-medium px-2 py-0.5 rounded-full"
									:class="probabilityStyle[item.probability]">
									{{ probabilityLabel[item.probability] }}
								</span>
								<span class="text-xs font-medium px-2 py-0.5 rounded-full"
									:class="careTypeStyle[item.careType]">
									{{ careTypeLabel[item.careType] }}
								</span>
							</div>
						</div>
					</CardHeader>
					<CardContent class="flex flex-col gap-4">
						<div>
							<p class="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-1">Why</p>
							<p class="text-sm">{{ item.motivation }}</p>
						</div>
						<div>
							<p class="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-1">Recommendations</p>
							<p class="text-sm">{{ item.recommendations }}</p>
						</div>
					</CardContent>
				</Card>
			</div>
		</template>

		<template v-else>
			<p class="text-muted-foreground">Diagnosis not found.</p>
		</template>
	</div>
</template>
