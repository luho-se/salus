<script setup lang="ts">
import { useRouter } from 'vue-router';
import { toast } from 'vue-sonner';
import { Sidebar, SidebarContent, SidebarFooter, SidebarGroup, SidebarGroupContent, SidebarGroupLabel, SidebarHeader, SidebarMenu, SidebarMenuButton, SidebarMenuItem, SidebarRail, useSidebar } from './ui/sidebar';
import { CookingPot, Carrot, LogOut, LayoutGrid } from 'lucide-vue-next';

const router = useRouter()

// @todo check
const menuItems = [
	{
		title: "Project 1",
		projectId: 1,
		icon: CookingPot
	},
	{
		title: "Project 2",
		projectId: 2,
		icon: Carrot
	}

]

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
			<RouterLink to="/" as-child>
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
						<SidebarMenuItem v-for="item in menuItems" :key="item.title">
							<RouterLink :to="{ name: 'project', params: { id: item.projectId } }" as-child>
								<SidebarMenuButton as-child class="cursor-pointer">
									<div>
										<component :is="item.icon" />
										<span>{{ item.title }}</span>
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
