<script setup lang="ts">
import CreateProjectForm, { CreateProjectValues } from '@/components/CreateProjectForm.vue';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useProjectStore } from '@/stores/projects.store';
import { ProjectStep } from '@/types/types';
import { FolderPlus, Plus } from 'lucide-vue-next';
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { toast } from 'vue-sonner';

const router = useRouter()
const projectStore = useProjectStore()

const dialogRef = ref()

onMounted(() => projectStore.loadProjects())

function trigger() {
	dialogRef.value.toggleDialog()
}

const handleNewProject = async (values: CreateProjectValues) => {
	const result = await projectStore.createProject(values)
	if (!result.success) {
		toast.error(projectStore.errorState || 'Failed to create project')
		return
	}
	trigger()
	router.push(`/project/${result.project!.id}`)
}

function stepLabel(step: ProjectStep): string {
	if (step === 'INITIAL_PROMPT') return 'Awaiting description'
	if (step === 'INITIAL_QUESTIONS') return 'Questions ready'
	return 'Diagnosis ready'
}

function formatDate(iso: string): string {
	const date = new Date(iso)
	const diff = Date.now() - date.getTime()
	const minutes = Math.floor(diff / 60000)
	if (minutes < 1) return 'just now'
	if (minutes < 60) return `${minutes}m ago`
	const hours = Math.floor(minutes / 60)
	if (hours < 24) return `${hours}h ago`
	return `${Math.floor(hours / 24)}d ago`
}
</script>

<template>
	<CreateProjectForm ref="dialogRef" @submit="handleNewProject" />
	<div class="flex flex-col gap-10 grow p-10 h-full overflow-hidden max-h-screen">
		<div class="flex flex-row justify-between">
			<div class="flex flex-col">
				<div class="text-3xl text-secondary-foreground">Your projects</div>
				<div class="text-muted-foreground">{{ projectStore.projects.length }} project{{ projectStore.projects.length === 1 ? '' : 's' }}</div>
			</div>
			<div>
				<Button size="lg" class="hover:cursor-pointer" @click="trigger">
					<Plus /> New project
				</Button>
			</div>
		</div>

		<div class="grid grid-cols-2 gap-6 overflow-y-auto min-h-0 flex-1 pb-4">
			<Card
				v-for="project in projectStore.projects"
				:key="project.id"
				class="min-h-40 cursor-pointer hover:shadow-md transition-shadow"
				@click="router.push(`/project/${project.id}`)"
			>
				<CardHeader>
					<CardTitle>{{ project.title }}</CardTitle>
					<CardDescription>{{ stepLabel(project.step) }} · {{ formatDate(project.updatedAt) }}</CardDescription>
				</CardHeader>
				<CardContent>
					<p v-if="project.initialPrompt" class="text-sm text-muted-foreground line-clamp-3">{{ project.initialPrompt }}</p>
					<p v-else class="text-sm text-muted-foreground italic">No description yet</p>
				</CardContent>
			</Card>

			<!-- Empty state -->
			<template v-if="!projectStore.loading && projectStore.projects.length === 0">
				<div class="col-span-2 flex flex-col items-center justify-center py-20 text-muted-foreground gap-2">
					<FolderPlus class="w-12 h-12 opacity-30" />
					<p>No projects yet</p>
				</div>
			</template>
		</div>

		<div class="flex flex-col">
			<Card class="min-h-40 outline-dashed flex flex-col justify-center">
				<CardHeader>
					<CardTitle class="text-center flex flex-col justify-center">
						<div class="flex flex-row justify-center pb-2">
							<FolderPlus class="w-14 h-14" />
						</div>
						<div>Start a new project</div>
					</CardTitle>
					<CardDescription class="text-center">Describe your situation and we'll guide the analysis</CardDescription>
					<CardContent class="flex flex-row justify-center pt-5">
						<Button size="lg" class="hover:cursor-pointer" @click="trigger">
							<Plus /> Create project
						</Button>
					</CardContent>
				</CardHeader>
			</Card>
		</div>
	</div>
</template>
