import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { Book } from '@/types/Book'
import { BookStatus } from '@/types/Book'
import apiClient from '@/services/api'
import { toast } from 'vue-sonner'

export const useBookStore = defineStore('book', () => {
  const books = ref<Book[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const searchQuery = ref('')

  const filteredBooks = computed(() => {
    const query = searchQuery.value.toLowerCase().trim()
    if (!query) return books.value

    return books.value.filter(
      book =>
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
    const isBorrowing = originalStatus === BookStatus.Available
    const endpoint = isBorrowing ? 'borrow' : 'return'

    book.status = isBorrowing ? BookStatus.Borrowed : BookStatus.Available

    try {
      await apiClient.patch(`/books/${bookId}/${endpoint}`)
      toast.success(isBorrowing ? 'Book borrowed successfully!' : 'Book returned successfully!')

      // Refresh stats after successful status change
      const { useStatsStore } = await import('@/stores/statsStore')
      const statsStore = useStatsStore()
      await statsStore.fetchStatistics()
    } catch (_err) {
      book.status = originalStatus
      error.value = 'Failed to update book status'
      toast.error('Failed to update book status')
    }
  }

  async function addBook(bookData: {
    title: string
    author: string
    isbn?: string
  }) {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.post<Book>('/books/', bookData)
      books.value.push(response.data)
      toast.success('Book added successfully!')
    } catch (_err) {
      error.value = 'Failed to create book'
      toast.error('Failed to create book')
      throw _err
    } finally {
      isLoading.value = false
    }
  }

  async function updateBook(
    bookId: number,
    bookData: Partial<{ title: string; author: string; isbn: string }>
  ) {
    error.value = null

    try {
      const response = await apiClient.put<Book>(`/books/${bookId}`, bookData)
      const index = books.value.findIndex(b => b.id === bookId)
      if (index !== -1) {
        books.value[index] = response.data
      }
      toast.success('Book updated successfully!')
    } catch (_err) {
      error.value = 'Failed to update book'
      toast.error('Failed to update book')
      throw _err
    }
  }

  async function deleteBook(bookId: number) {
    error.value = null

    try {
      await apiClient.delete(`/books/${bookId}`)
      books.value = books.value.filter(b => b.id !== bookId)
      toast.success('Book deleted successfully!')
    } catch (_err) {
      error.value = 'Failed to delete book'
      toast.error('Failed to delete book')
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
    deleteBook,
  }
})
