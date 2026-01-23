<script setup lang="ts">
import type { Book } from '@/types/Book'
import { BookStatus } from '@/types/Book'
import { useBookStore } from '@/stores/bookStore'
import { useAuthStore } from '@/stores/authStore'

const props = defineProps<{
  book: Book
}>()

const emit = defineEmits<{
  edit: [book: Book]
  delete: [bookId: number]
}>()

const bookStore = useBookStore()
const authStore = useAuthStore()

const getStatusColor = (status: BookStatus) => {
  return status === BookStatus.Available
    ? 'bg-green-100 text-green-800'
    : 'bg-yellow-100 text-yellow-800'
}

const getButtonClass = (status: BookStatus) => {
  return status === BookStatus.Available
    ? 'bg-green-600 hover:bg-green-700'
    : 'bg-orange-600 hover:bg-orange-700'
}

const getButtonLabel = (status: BookStatus) => {
  return status === BookStatus.Available ? 'Borrow' : 'Return'
}

function handleDelete() {
  if (
    window.confirm(`Are you sure you want to delete "${props.book.title}"?`)
  ) {
    emit('delete', props.book.id)
  }
}

function handleImageError(event: globalThis.Event) {
  const target = event.target as globalThis.HTMLImageElement
  target.style.display = 'none'
}
</script>

<template>
  <div
    :data-testid="`book-item-${book.id}`"
    class="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 overflow-hidden border border-gray-200 flex flex-col h-full"
  >
    <div class="relative w-full h-64 bg-gray-100">
      <div
        v-if="book.cover_image"
        class="w-full h-full flex items-center justify-center overflow-hidden"
      >
        <img
          :src="book.cover_image"
          :alt="`Cover of ${book.title}`"
          class="h-full w-full object-contain"
          @error="handleImageError"
        />
      </div>
      <div
        v-else
        class="w-full h-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center"
      >
        <svg
          class="w-16 h-16 text-gray-400"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            fill-rule="evenodd"
            d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a1 1 0 110 2h-3a1 1 0 01-1-1v-2a1 1 0 00-1-1H9a1 1 0 00-1 1v2a1 1 0 01-1 1H4a1 1 0 110-2V4zm3 1h2v2H7V5zm2 4H7v2h2V9zm2-4h2v2h-2V5zm2 4h-2v2h2V9z"
            clip-rule="evenodd"
          />
        </svg>
      </div>
      <span
        :class="getStatusColor(book.status)"
        class="absolute top-2 right-2 px-3 py-1 rounded-full text-xs font-semibold shadow-md"
      >
        {{ book.status }}
      </span>
    </div>

    <div class="p-4 flex flex-col flex-1">
      <h3
        class="text-lg font-bold text-gray-900 mb-3 line-clamp-2"
        :title="book.title"
      >
        {{ book.title }}
      </h3>

      <div class="space-y-2 text-sm text-gray-600">
        <div class="flex items-center">
          <svg
            class="w-4 h-4 mr-2 text-gray-400"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fill-rule="evenodd"
              d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
              clip-rule="evenodd"
            />
          </svg>
          <span class="font-medium">{{ book.author }}</span>
        </div>

        <div class="flex items-center">
          <svg
            class="w-4 h-4 mr-2 text-gray-400"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fill-rule="evenodd"
              d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a1 1 0 110 2h-3a1 1 0 01-1-1v-2a1 1 0 00-1-1H9a1 1 0 00-1 1v2a1 1 0 01-1 1H4a1 1 0 110-2V4zm3 1h2v2H7V5zm2 4H7v2h2V9zm2-4h2v2h-2V5zm2 4h-2v2h2V9z"
              clip-rule="evenodd"
            />
          </svg>
          <span>{{ book.isbn || 'No ISBN' }}</span>
        </div>

        <div
          v-if="book.summary"
          class="pt-2 text-gray-700 text-sm italic border-t border-gray-100"
        >
          {{ book.summary }}
        </div>

        <div
          class="flex items-center text-xs text-gray-400 pt-2 border-t border-gray-100"
        >
          <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path
              fill-rule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
              clip-rule="evenodd"
            />
          </svg>
          Added {{ new Date(book.created_at).toLocaleDateString() }}
        </div>
      </div>

      <div class="mt-auto pt-3 border-t border-gray-100 space-y-2">
        <button
          v-if="authStore.isAuthenticated"
          :class="getButtonClass(book.status)"
          class="w-full text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
          data-testid="toggle-status-btn"
          @click="bookStore.toggleStatus(book.id)"
        >
          {{ getButtonLabel(book.status) }}
        </button>

        <div v-if="authStore.isAdmin" class="flex gap-2">
          <button
            class="flex-1 px-3 py-2 border border-blue-600 text-blue-600 rounded-lg text-sm font-semibold hover:bg-blue-50 transition-colors"
            data-testid="edit-btn"
            @click="emit('edit', book)"
          >
            Edit
          </button>
          <button
            class="flex-1 px-3 py-2 border border-red-600 text-red-600 rounded-lg text-sm font-semibold hover:bg-red-50 transition-colors"
            data-testid="delete-btn"
            @click="handleDelete"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
