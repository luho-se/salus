import PrivateLayout from '@/layouts/PrivateLayout.vue'
import HomeView from '@/views/HomeView.vue'
import ProjectDiagnosisView from '@/views/ProjectDiagnosisView.vue'
import ProjectQuestionsView from '@/views/ProjectQuestionsView.vue'
import ProjectSummaryView from '@/views/ProjectSummaryView.vue'
import ProjectView from '@/views/ProjectView.vue'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
	history: createWebHistory(import.meta.env.BASE_URL),
	routes: [
		{
			path: '/',
			name: 'app',
			component: PrivateLayout,
			children: [
				{
					path: 'home',
					name: 'home',
					component: HomeView,
				},
				{
					path: 'project/:id',
					name: 'project',
					component: ProjectView,
				},
				{
					path: 'project/:id/questions',
					name: 'project-questions',
					component: ProjectQuestionsView,
				},
				{
					path: 'project/:id/summary',
					name: 'project-summary',
					component: ProjectSummaryView,
				},
				{
					path: 'project/:id/diagnosis/:diagnosisId',
					name: 'project-diagnosis',
					component: ProjectDiagnosisView,
				},
			],
		}
	],
})

export default router
