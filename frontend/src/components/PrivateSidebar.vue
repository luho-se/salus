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
	<Sidebar class="font-lato select-none" collapsible="icon" @click="handleSidebarClick">
		<SidebarHeader class="bg-light-gold-100">
			<RouterLink to="/" as-child>
				<div class="logo-parent flex flex-row justify-center py-5 items-center gap-1">
					<div class="logo-main" :class="{ collapsed: state === 'collapsed' }">
						<span class="text-royal-gold-400 font-lato font-extrabold tracking-[-0.35rem]">
							N
						</span>
						<span class="logo-sub text-royal-gold-400 font-lato font-extrabold tracking-tighter">
							utri
						</span>
					</div>
					<div class="logo-main" :class="{ collapsed: state === 'collapsed' }">
						<span class=" text-golden-orange-400 font-lato font-extrabold tracking-[-0.35rem] italic">
							P
						</span>
						<span class="logo-sub text-golden-orange-400 font-lato font-extrabold tracking-tighter italic">
							e
						</span>
					</div>
				</div>
			</RouterLink>
		</SidebarHeader>
		<SidebarContent class="bg-light-gold-100 overflow-x-hidden">
			<SidebarGroup>
				<SidebarGroupLabel>Navigation</SidebarGroupLabel>
				<SidebarGroupContent>
					<SidebarMenu>
						<SidebarMenuItem>
							<RouterLink :to="{ name: 'home' }" as-child>
								<SidebarMenuButton as-child class="hover:bg-light-gold-200 cursor-pointer">
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
								<SidebarMenuButton as-child class="hover:bg-light-gold-200 cursor-pointer">
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
	transform: scale(0.6);
}

.logo-main.collapsed:nth-of-type(1) {
	transform: scale(0.6) translateX(60%);
}

.logo-main.collapsed:nth-of-type(2) {
	transform: scale(0.6) translateX(-135%);
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
