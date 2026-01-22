import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { Book } from '@/types/Book'
import { BookStatus } from '@/types/Book'
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

  async function toggleStatus(bookId: number) {
    const book = books.value.find(b => b.id === bookId)
    if (!book) return

    const originalStatus = book.status
    const newStatus = originalStatus === BookStatus.Available
      ? BookStatus.Borrowed
      : BookStatus.Available

    book.status = newStatus

    try {
      await apiClient.put(`/books/${bookId}`, { status: newStatus })
    } catch (_err) {
      book.status = originalStatus
      error.value = 'Failed to update book status'
    }
  }

  async function addBook(bookData: { title: string; author: string; isbn?: string }) {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.post<Book>('/books/', bookData)
      books.value.push(response.data)
    } catch (_err) {
      error.value = 'Failed to create book'
      throw _err
    } finally {
      isLoading.value = false
    }
  }

  async function updateBook(bookId: number, bookData: Partial<{ title: string; author: string; isbn: string }>) {
    error.value = null

    try {
      const response = await apiClient.put<Book>(`/books/${bookId}`, bookData)
      const index = books.value.findIndex(b => b.id === bookId)
      if (index !== -1) {
        books.value[index] = response.data
      }
    } catch (_err) {
      error.value = 'Failed to update book'
      throw _err
    }
  }

  async function deleteBook(bookId: number) {
    error.value = null

    try {
      await apiClient.delete(`/books/${bookId}`)
      books.value = books.value.filter(b => b.id !== bookId)
    } catch (_err) {
      error.value = 'Failed to delete book'
      throw _err
    }
  }

  return {
    books,
    isLoading,
    error,
    searchQuery,
    filteredBooks,
    fetchBooks,
    toggleStatus,
    addBook,
    updateBook,
    deleteBook
  }
})
