<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod'
import { Form, Field as VeeField } from 'vee-validate'
import { h, ref } from 'vue'

import * as z from 'zod'
import { Button } from '@/components/ui/button'
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle,
	DialogTrigger,
} from '@/components/ui/dialog'
import {
	Field,
	FieldDescription,
	FieldError,
	FieldGroup,
	FieldLabel,
} from '@/components/ui/field'
import { Input } from '@/components/ui/input'

const schema = z.object({
	title: z.string().min(2).max(50),
})

const formSchema = toTypedSchema(schema);

export type CreateProjectValues = z.infer<typeof schema>

function onSubmit(values: any) {
	emit('submit', values)
}

const emit = defineEmits<{
	(e: 'submit', values: CreateProjectValues): void
}>()

const open = ref(false)

function toggleDialog() {
	open.value = !open.value
}

defineExpose({
	toggleDialog,
})

</script>

<template>
	<Form v-slot="{ handleSubmit }" as="" keep-values :validation-schema="formSchema">
		<Dialog v-model:open="open">
			<DialogTrigger as-child>
			</DialogTrigger>
			<DialogContent class="sm:max-w-106.25">
				<DialogHeader>
					<DialogTitle>Create a new project</DialogTitle>
					<DialogDescription>
						Create a new project for a health issue you are having.
					</DialogDescription>
				</DialogHeader>

				<form id="dialogForm" @submit="handleSubmit($event, onSubmit)" :validation-schema="formSchema">
					<FieldGroup>
						<VeeField v-slot="{ componentField, errors }" name="title">
							<Field :data-invalid="!!errors.length">
								<FieldLabel for="title">
									Project title
								</FieldLabel>
								<Input id="title" type="text" placeholder="e.g. Pain in the left leg"
									v-bind="componentField" />
								<FieldError v-if="errors.length" :errors="errors" />
							</Field>
						</VeeField>
					</FieldGroup>
				</form>

				<DialogFooter>
					<Button type="submit" form="dialogForm" class="hover:cursor-pointer">
						Create
					</Button>
				</DialogFooter>
			</DialogContent>
		</Dialog>
	</Form>
</template>
