import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { Book } from '@/types/Book'
import apiClient from '@/services/api'

export const useBookStore = defineStore('book', () => {
  const books = ref<Book[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function fetchBooks() {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.get<Book[]>('/books')
      books.value = response.data
    } catch (err) {
      error.value = 'Failed to fetch books'
      books.value = []
    } finally {
      isLoading.value = false
    }
  }

  return { books, isLoading, error, fetchBooks }
})
