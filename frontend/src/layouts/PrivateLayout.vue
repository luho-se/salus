<script setup lang="ts">
import PrivateSidebar from '@/components/PrivateSidebar.vue';
import { SidebarProvider } from '@/components/ui/sidebar';


</script>


<template>
	<div class="h-full">
		<SidebarProvider class="h-full">
			<PrivateSidebar />
			<main class="flex-1 flex h-full">
				<RouterView />
			</main>
		</SidebarProvider>
	</div>
</template>
