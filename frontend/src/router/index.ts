import PrivateLayout from '@/layouts/PrivateLayout.vue'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
	history: createWebHistory(import.meta.env.BASE_URL),
	routes: [
		{
			path: '/',
			name: '',
			component: PrivateLayout,
			children: [
				{
					path: 'home',
					name: 'home',
					component: RecipesView,
				},
				{
					path: 'project/:id',
					name: 'project',
					component: IngredientsView,
				},
				{
					path: 'project/:id/questions',
					name: 'project-questions',
					component: RecipeEditView,
				},
				{
					path: 'project/:id/diagnosis',
					name: 'project-diagnosis',
					component: RecipeEditView,
				},
			],
		}
	],
})

// Navigation guard
router.beforeEach(async (to, from, next) => {
	const authStore = useAuthStore()
	await authStore.checkAuth()
	// Check for illegal route configuration
	if (to.meta.requiresAuth && to.meta.redirectIfAuthenticated) {
		console.error('Route config error: Route cannot require auth and redirect if authenticated')
		next('/login')
		return
	}

	// Redirect unauthenticated users from private routes
	if (to.meta.requiresAuth && !authStore.isAuthenticated) {
		next('/login')
		return
	}

	// Redirect authenticated users from public routes with redirectIfAuthenticated
	if (to.meta.redirectIfAuthenticated && authStore.isAuthenticated) {
		next('/app/recipes')
		return
	}

	// Check that we actually enter a valid site and not a "page parent"
	if (to.name === 'app') {
		next('/app/recipes')
		return
	}

	next()
})

export default router
