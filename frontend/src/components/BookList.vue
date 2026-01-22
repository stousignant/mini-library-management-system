<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useBookStore } from '@/stores/bookStore'
import BookCard from './BookCard.vue'
import BookFormModal from './BookFormModal.vue'
import type { Book } from '@/types/Book'

const bookStore = useBookStore()
const isModalOpen = ref(false)
const bookToEdit = ref<Book | undefined>(undefined)

onMounted(() => {
  bookStore.fetchBooks()
})

function openAddModal() {
  bookToEdit.value = undefined
  isModalOpen.value = true
}

function openEditModal(book: Book) {
  bookToEdit.value = book
  isModalOpen.value = true
}

function closeModal() {
  isModalOpen.value = false
  bookToEdit.value = undefined
}

async function handleSubmit(data: {
  title: string
  author: string
  isbn?: string
}) {
  try {
    if (bookToEdit.value) {
      await bookStore.updateBook(bookToEdit.value.id, data)
    } else {
      await bookStore.addBook(data)
    }
    closeModal()
  } catch (_err) {
    // Error already set in store
  }
}

async function handleDelete(bookId: number) {
  try {
    await bookStore.deleteBook(bookId)
  } catch (_err) {
    // Error already set in store
  }
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
        <div
          class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mb-4"
        ></div>
        <p class="text-gray-600">Loading books...</p>
      </div>
    </div>

    <div
      v-else-if="bookStore.error"
      data-testid="error-state"
      class="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800"
    >
      <svg
        class="inline-block w-5 h-5 mr-2"
        fill="currentColor"
        viewBox="0 0 20 20"
      >
        <path
          fill-rule="evenodd"
          d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
          clip-rule="evenodd"
        />
      </svg>
      {{ bookStore.error }}
    </div>

    <div v-else data-testid="book-list">
      <div class="mb-6 flex gap-4">
        <input
          v-model="bookStore.searchQuery"
          type="text"
          placeholder="Search by title or author..."
          class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          data-testid="search-input"
        />
        <button
          class="px-6 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors whitespace-nowrap"
          data-testid="add-book-btn"
          @click="openAddModal"
        >
          Add Book
        </button>
      </div>

      <div
        v-if="bookStore.filteredBooks.length === 0"
        class="text-center py-12 text-gray-500"
      >
        <svg
          class="mx-auto h-12 w-12 text-gray-400 mb-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
          />
        </svg>
        <p class="text-lg font-medium">
          {{
            bookStore.searchQuery
              ? 'No books match your search'
              : 'No books found'
          }}
        </p>
        <p class="text-sm mt-1">
          {{
            bookStore.searchQuery
              ? 'Try a different search term'
              : 'Add your first book to get started'
          }}
        </p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        <BookCard
          v-for="book in bookStore.filteredBooks"
          :key="book.id"
          :book="book"
          @edit="openEditModal"
          @delete="handleDelete"
        />
      </div>
    </div>

    <BookFormModal
      :is-open="isModalOpen"
      :book-to-edit="bookToEdit"
      @close="closeModal"
      @submit="handleSubmit"
    />
  </div>
</template>
