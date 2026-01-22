<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import type { Book } from '@/types/Book'

const props = defineProps<{
  isOpen: boolean
  bookToEdit?: Book
}>()

const emit = defineEmits<{
  close: []
  submit: [data: { title: string; author: string; isbn?: string }]
}>()

const title = ref('')
const author = ref('')
const isbn = ref('')

const isEditMode = computed(() => !!props.bookToEdit)

watch(
  () => props.bookToEdit,
  book => {
    if (book) {
      title.value = book.title
      author.value = book.author
      isbn.value = book.isbn || ''
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
}

function handleSubmit() {
  if (!title.value.trim() || !author.value.trim()) {
    return
  }

  emit('submit', {
    title: title.value.trim(),
    author: author.value.trim(),
    isbn: isbn.value.trim() || undefined,
  })

  resetForm()
}

function handleClose() {
  resetForm()
  emit('close')
}
</script>

<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    @click.self="handleClose"
  >
    <div class="bg-white rounded-lg p-6 w-full max-w-md">
      <h2 class="text-2xl font-bold mb-4">
        {{ isEditMode ? 'Edit Book' : 'Add New Book' }}
      </h2>

      <form @submit.prevent="handleSubmit">
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Title <span class="text-red-500">*</span>
          </label>
          <input
            v-model="title"
            type="text"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            data-testid="title-input"
          />
        </div>

        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Author <span class="text-red-500">*</span>
          </label>
          <input
            v-model="author"
            type="text"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            data-testid="author-input"
          />
        </div>

        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            ISBN
          </label>
          <input
            v-model="isbn"
            type="text"
            :disabled="isEditMode"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            data-testid="isbn-input"
          />
          <p v-if="isEditMode" class="text-xs text-gray-500 mt-1">
            ISBN cannot be changed after creation
          </p>
        </div>

        <div class="flex gap-3">
          <button
            type="button"
            class="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            @click="handleClose"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            data-testid="submit-btn"
          >
            {{ isEditMode ? 'Save Changes' : 'Add Book' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
