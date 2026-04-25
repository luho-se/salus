<script setup lang="ts">
import PrivateSidebar from '@/components/PrivateSidebar.vue';
import { SidebarProvider } from '@/components/ui/sidebar';


</script>


<template>
	<div>
		<SidebarProvider>
			<PrivateSidebar />
			<main class="flex-1 flex">
				<RouterView />
			</main>
		</SidebarProvider>
	</div>
</template>
