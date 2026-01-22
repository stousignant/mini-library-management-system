<script setup lang="ts">
import type { Book } from '@/types/Book'
import { BookStatus } from '@/types/Book'
import { useBookStore } from '@/stores/bookStore'

defineProps<{
  book: Book
}>()

const bookStore = useBookStore()

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
</script>

<template>
  <div
    :data-testid="`book-item-${book.id}`"
    class="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 overflow-hidden border border-gray-200"
  >
    <div class="p-6">
      <div class="flex items-start justify-between mb-4">
        <h3 class="text-xl font-bold text-gray-900 flex-1 pr-2">
          {{ book.title }}
        </h3>
        <span
          :class="getStatusColor(book.status)"
          class="px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap"
        >
          {{ book.status }}
        </span>
      </div>

      <div class="space-y-2 text-sm text-gray-600">
        <div class="flex items-center">
          <svg class="w-4 h-4 mr-2 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
          </svg>
          <span class="font-medium">{{ book.author }}</span>
        </div>

        <div class="flex items-center">
          <svg class="w-4 h-4 mr-2 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a1 1 0 110 2h-3a1 1 0 01-1-1v-2a1 1 0 00-1-1H9a1 1 0 00-1 1v2a1 1 0 01-1 1H4a1 1 0 110-2V4zm3 1h2v2H7V5zm2 4H7v2h2V9zm2-4h2v2h-2V5zm2 4h-2v2h2V9z" clip-rule="evenodd" />
          </svg>
          <span>{{ book.isbn || 'No ISBN' }}</span>
        </div>

        <div class="flex items-center text-xs text-gray-400 pt-2 border-t border-gray-100">
          <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
          </svg>
          Added {{ new Date(book.created_at).toLocaleDateString() }}
        </div>
      </div>

      <div class="mt-4 pt-4 border-t border-gray-100">
        <button
          @click="bookStore.toggleStatus(book.id)"
          :class="getButtonClass(book.status)"
          class="w-full text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
          data-testid="toggle-status-btn"
        >
          {{ getButtonLabel(book.status) }}
        </button>
      </div>
    </div>
  </div>
</template>
