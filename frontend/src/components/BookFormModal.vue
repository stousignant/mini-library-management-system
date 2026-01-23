<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import type { Book } from '@/types/Book'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'

const props = defineProps<{
  isOpen: boolean
  bookToEdit?: Book
}>()

const emit = defineEmits<{
  close: []
  submit: [
    data: {
      title: string
      author: string
      isbn?: string
      cover_image?: string
      summary?: string
    },
  ]
}>()

const title = ref('')
const author = ref('')
const isbn = ref('')
const coverImage = ref('')
const summary = ref('')

const isEditMode = computed(() => !!props.bookToEdit)

watch(
  () => props.bookToEdit,
  book => {
    if (book) {
      title.value = book.title
      author.value = book.author
      isbn.value = book.isbn || ''
      coverImage.value = book.cover_image || ''
      summary.value = book.summary || ''
    } else {
      resetForm()
    }
  },
  { immediate: true }
)

function resetForm() {
  title.value = ''
  author.value = ''
  isbn.value = ''
  coverImage.value = ''
  summary.value = ''
}

function handleSubmit() {
  if (!title.value.trim() || !author.value.trim()) {
    return
  }

  emit('submit', {
    title: title.value.trim(),
    author: author.value.trim(),
    isbn: isbn.value.trim() || undefined,
    cover_image: coverImage.value.trim() || undefined,
    summary: summary.value.trim() || undefined,
  })

  resetForm()
}

function handleClose() {
  resetForm()
  emit('close')
}

function handleOpenChange(open: boolean) {
  if (!open) {
    handleClose()
  }
}
</script>

<template>
  <Dialog :open="isOpen" @update:open="handleOpenChange">
    <DialogContent class="sm:max-w-md">
      <DialogHeader>
        <DialogTitle>
          {{ isEditMode ? 'Edit Book' : 'Add New Book' }}
        </DialogTitle>
        <DialogDescription>
          {{
            isEditMode
              ? 'Update the book information below.'
              : 'Fill in the details to add a new book to the library.'
          }}
        </DialogDescription>
      </DialogHeader>

      <form @submit.prevent="handleSubmit">
        <div class="space-y-4">
          <div class="space-y-2">
            <Label for="title">
              Title <span class="text-destructive">*</span>
            </Label>
            <Input
              id="title"
              v-model="title"
              type="text"
              required
              data-testid="title-input"
            />
          </div>

          <div class="space-y-2">
            <Label for="author">
              Author <span class="text-destructive">*</span>
            </Label>
            <Input
              id="author"
              v-model="author"
              type="text"
              required
              data-testid="author-input"
            />
          </div>

          <div class="space-y-2">
            <Label for="isbn">ISBN</Label>
            <Input
              id="isbn"
              v-model="isbn"
              type="text"
              :disabled="isEditMode"
              data-testid="isbn-input"
            />
            <p v-if="isEditMode" class="text-xs text-muted-foreground">
              ISBN cannot be changed after creation
            </p>
          </div>

          <div class="space-y-2">
            <Label for="coverImage">Cover Image URL</Label>
            <Input
              id="coverImage"
              v-model="coverImage"
              type="url"
              placeholder="https://example.com/cover.jpg"
              data-testid="cover-image-input"
            />
          </div>

          <div class="space-y-2">
            <Label for="summary">Summary</Label>
            <Textarea
              id="summary"
              v-model="summary"
              rows="3"
              placeholder="Brief description or publisher information"
              data-testid="summary-input"
            />
          </div>
        </div>

        <DialogFooter class="mt-6">
          <Button type="button" variant="outline" @click="handleClose">
            Cancel
          </Button>
          <Button type="submit" data-testid="submit-btn">
            {{ isEditMode ? 'Save Changes' : 'Add Book' }}
          </Button>
        </DialogFooter>
      </form>
    </DialogContent>
  </Dialog>
</template>
