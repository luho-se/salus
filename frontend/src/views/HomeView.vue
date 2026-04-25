<script setup lang="ts">
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { FolderPlus, Plus } from 'lucide-vue-next';




</script>

<template>
	<div class="flex flex-col gap-10 grow p-10 h-full overflow-hidden max-h-screen">
		<div class="flex flex-row justify-between">
			<div class="flex flex-col">
				<div class="text-3xl text-secondary-foreground">Your projects</div>
				<div class="text-muted-foreground">3 active - last updated 2 hours ago</div>
			</div>
			<div>
				<Button size="lg" class="hover:cursor-pointer">
					<Plus /> New project
				</Button>
			</div>
		</div>
		<div class="grid grid-cols-2 gap-12 overflow-y-auto min-h-0 flex-1 pb-4">
			<Card v-for="i in 10" class="min-h-50">
				<CardHeader>
					<CardTitle>Card Title</CardTitle>
					<CardDescription>Card Description</CardDescription>
				</CardHeader>
				<CardContent>
					<p>Card Content</p>
				</CardContent>
				<CardFooter>
					<p>Card Footer</p>
				</CardFooter>
			</Card>
		</div>
		<div class="flex flex-col ">
			<Card class="min-h-50 outline-dashed flex flex-col justify-center">
				<CardHeader>
					<CardTitle class="text-center flex flex-col justify-center">
						<div class="flex flex-row justify-center pb-2">
							<FolderPlus class="w-14 h-14" />
						</div>
						<div>Start a new project</div>
					</CardTitle>
					<CardDescription class="text-center">Describe your situation and we'll guide the analysis
					</CardDescription>
					<CardContent class="flex flex-row justify-center pt-5">
						<Button size="lg" class="hover:cursor-pointer">
							<Plus /> Create project
						</Button>
					</CardContent>
				</CardHeader>
			</Card>
		</div>

	</div>
</template>
