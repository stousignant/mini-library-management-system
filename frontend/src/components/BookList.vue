<script setup lang="ts">
import { onMounted } from 'vue'
import { useBookStore } from '@/stores/bookStore'
import { BookStatus } from '@/types/Book'

const bookStore = useBookStore()

onMounted(() => {
  bookStore.fetchBooks()
})

const getStatusColor = (status: BookStatus) => {
  return status === BookStatus.Available
    ? 'bg-green-100 text-green-800'
    : 'bg-yellow-100 text-yellow-800'
}
</script>

<template>
  <div class="book-list">
    <div
      v-if="bookStore.isLoading"
      data-testid="loading-state"
      class="flex items-center justify-center py-12"
    >
      <div class="text-center">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mb-4"></div>
        <p class="text-gray-600">Loading books...</p>
      </div>
    </div>

    <div
      v-else-if="bookStore.error"
      data-testid="error-state"
      class="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800"
    >
      <svg class="inline-block w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
      </svg>
      {{ bookStore.error }}
    </div>

    <div v-else data-testid="book-list">
      <div v-if="bookStore.books.length === 0" class="text-center py-12 text-gray-500">
        <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
        <p class="text-lg font-medium">No books found</p>
        <p class="text-sm mt-1">Add your first book to get started</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="book in bookStore.books"
          :key="book.id"
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
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
