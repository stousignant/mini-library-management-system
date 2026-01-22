import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { Book } from '@/types/Book'
import apiClient from '@/services/api'

export const useBookStore = defineStore('book', () => {
  const books = ref<Book[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const searchQuery = ref('')

  const filteredBooks = computed(() => {
    const query = searchQuery.value.toLowerCase().trim()
    if (!query) return books.value

    return books.value.filter(book =>
      book.title.toLowerCase().includes(query) ||
      book.author.toLowerCase().includes(query)
    )
  })

  async function fetchBooks() {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.get<Book[]>('/books/')
      books.value = response.data
    } catch (_err) {
      error.value = 'Failed to fetch books'
      books.value = []
    } finally {
      isLoading.value = false
    }
  }

  return { books, isLoading, error, searchQuery, filteredBooks, fetchBooks }
})
