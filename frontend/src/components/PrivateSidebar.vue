<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router';
import { Sidebar, SidebarContent, SidebarGroup, SidebarGroupContent, SidebarGroupLabel, SidebarHeader, SidebarMenu, SidebarMenuButton, SidebarMenuItem, SidebarRail, useSidebar } from './ui/sidebar';
import { FolderOpen, Folder, LayoutGrid } from 'lucide-vue-next';
import { useProjectStore } from '@/stores/projects.store';
import { computed, onMounted } from 'vue';

const router = useRouter()
const route = useRoute()
const projectStore = useProjectStore()

const currentProjectId = computed(() => {
	const id = Number(route.params.id)
	return isNaN(id) ? null : id
})

onMounted(() => {
	if (!projectStore.projects.length) projectStore.loadProjects()
})

const recentProjects = computed(() => projectStore.projects.slice(0, 5))

const { state, toggleSidebar } = useSidebar();

const handleSidebarClick = (e: MouseEvent) => {
	const target = e.target as HTMLElement;
	const isInteractive = target.closest('a, button, [role="button"]');
	if (!isInteractive) {
		toggleSidebar();
	}
};



</script>

<template>
	<Sidebar class="select-none" collapsible="icon" @click="handleSidebarClick">
		<SidebarHeader class="">
			<RouterLink to="/home" as-child>
				<div class="text-center text-5xl font-title py-4">
					<div class="logo-main" :class="{ collapsed: state === 'collapsed' }">
						<span class="p-0 m-0 tracking-[-0.575rem]">
							s
						</span>
						<span class="logo-sub p-0 m-0">
							alus
						</span>
					</div>
				</div>
			</RouterLink>
		</SidebarHeader>
		<SidebarContent class=" overflow-x-hidden">
			<SidebarGroup>
				<SidebarGroupLabel>Navigation</SidebarGroupLabel>
				<SidebarGroupContent>
					<SidebarMenu>
						<SidebarMenuItem>
							<RouterLink :to="{ name: 'home' }" as-child>
								<SidebarMenuButton as-child class=" cursor-pointer">
									<div>
										<LayoutGrid />
										<span>All projects</span>
									</div>
								</SidebarMenuButton>
							</RouterLink>
						</SidebarMenuItem>
					</SidebarMenu>
				</SidebarGroupContent>

			</SidebarGroup>
			<SidebarGroup>
				<SidebarGroupLabel>Recent</SidebarGroupLabel>
				<SidebarGroupContent>
					<SidebarMenu>
						<SidebarMenuItem v-for="project in recentProjects" :key="project.id">
							<RouterLink :to="{ name: 'project', params: { id: project.id } }" as-child>
								<SidebarMenuButton as-child :isActive="project.id === currentProjectId" class="cursor-pointer">
									<div>
										<FolderOpen v-if="project.id === currentProjectId" />
										<Folder v-else />
										<span>{{ project.title }}</span>
									</div>
								</SidebarMenuButton>
							</RouterLink>
						</SidebarMenuItem>
					</SidebarMenu>
				</SidebarGroupContent>
			</SidebarGroup>
		</SidebarContent>
		<SidebarRail />
	</Sidebar>
</template>

<style lang="css" scoped>
.logo-main {
	font-size: 3rem;
	transition: transform 200ms ease;
	white-space: nowrap;
	transform-origin: center;
}

.logo-main.collapsed {
	transform: translateX(17.5%);
}

.logo-sub {
	overflow: hidden;
	opacity: 1;
	transition: transform 200ms ease, opacity 200ms ease;
}

.logo-main.collapsed .logo-sub {
	transform: scale(0);
	opacity: 0;
}
</style>
