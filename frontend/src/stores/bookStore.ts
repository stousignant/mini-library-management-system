import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { Book } from '@/types/Book'
import { BookStatus } from '@/types/Book'
import apiClient from '@/services/api'
import { toast } from 'vue-sonner'
import { STATS_POLLING_INTERVAL_MS } from '@/constants/global'

type SortOption = 'none' | 'title' | 'date'

export const useBookStore = defineStore('book', () => {
  const books = ref<Book[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const searchQuery = ref('')
  const showMyBooksOnly = ref(false)
  const showAvailableOnly = ref(false)
  const sortBy = ref<SortOption>('none')
  const filterUserId = ref<string | null>(null)
  let pollingInterval: ReturnType<typeof setInterval> | null = null

  const myBorrowedCount = computed(() => {
    if (!filterUserId.value) return 0

    return books.value.filter(book => book.borrowed_by === filterUserId.value)
      .length
  })

  const filteredBooks = computed(() => {
    let result = [...books.value]

    if (showMyBooksOnly.value && filterUserId.value) {
      result = result.filter(book => book.borrowed_by === filterUserId.value)
    }

    if (showAvailableOnly.value) {
      result = result.filter(book => {
        const statusStr = String(book.status).toUpperCase()
        return statusStr === 'AVAILABLE'
      })
    }

    const searchTerm = searchQuery.value.toLowerCase().trim()
    if (searchTerm) {
      result = result.filter(
        book =>
          book.title.toLowerCase().includes(searchTerm) ||
          book.author.toLowerCase().includes(searchTerm)
      )
    }

    if (sortBy.value === 'title') {
      result.sort((a, b) => a.title.localeCompare(b.title))
    } else if (sortBy.value === 'date') {
      result.sort(
        (a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      )
    }

    return result
  })

  async function fetchBooks(silent = false) {
    if (!silent) {
      isLoading.value = true
    }
    error.value = null

    try {
      const response = await apiClient.get<Book[]>('/books/')
      const newBooks = response.data

      if (silent) {
        const currentIds = new Set(books.value.map(b => b.id))
        const newIds = new Set(newBooks.map(b => b.id))
        const hasStructuralChanges =
          currentIds.size !== newIds.size ||
          [...currentIds].some(id => !newIds.has(id))

        if (hasStructuralChanges) {
          books.value = newBooks
        } else {
          newBooks.forEach(newBook => {
            const existingBook = books.value.find(b => b.id === newBook.id)
            if (existingBook && existingBook.status !== newBook.status) {
              existingBook.status = newBook.status
              existingBook.borrowed_by = newBook.borrowed_by
            }
          })
        }
      } else {
        books.value = newBooks
      }
    } catch (_err) {
      if (!silent) {
        error.value = 'Failed to fetch books'
        books.value = []
      }
    } finally {
      if (!silent) {
        isLoading.value = false
      }
    }
  }

  async function toggleStatus(bookId: number) {
    const book = books.value.find(b => b.id === bookId)
    if (!book) return

    const originalStatus = book.status
    const originalBorrowedBy = book.borrowed_by
    const isBorrowing = originalStatus === BookStatus.Available
    const endpoint = isBorrowing ? 'borrow' : 'return'

    book.status = isBorrowing ? BookStatus.Borrowed : BookStatus.Available

    try {
      const response = await apiClient.patch<Book>(
        `/books/${bookId}/${endpoint}`
      )
      book.status = response.data.status
      book.borrowed_by = response.data.borrowed_by
      toast.success(
        isBorrowing
          ? 'Book borrowed successfully!'
          : 'Book returned successfully!'
      )

      // Refresh stats after successful status change
      const { useStatsStore } = await import('@/stores/statsStore')
      const statsStore = useStatsStore()
      await statsStore.fetchStatistics()
    } catch (err: unknown) {
      // Revert optimistic update
      book.status = originalStatus
      book.borrowed_by = originalBorrowedBy

      // Show user-friendly error message
      let errorMessage = 'Failed to update book status'
      if (
        err &&
        typeof err === 'object' &&
        'response' in err &&
        err.response &&
        typeof err.response === 'object' &&
        'data' in err.response &&
        err.response.data &&
        typeof err.response.data === 'object' &&
        'detail' in err.response.data &&
        typeof err.response.data.detail === 'string'
      ) {
        errorMessage = err.response.data.detail
      }
      toast.error(errorMessage)
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

  function startPolling() {
    stopPolling()

    pollingInterval = setInterval(() => {
      fetchBooks(true)
    }, STATS_POLLING_INTERVAL_MS)
  }

  function stopPolling() {
    if (pollingInterval) {
      clearInterval(pollingInterval)
      pollingInterval = null
    }
  }

  return {
    books,
    isLoading,
    error,
    searchQuery,
    showMyBooksOnly,
    showAvailableOnly,
    sortBy,
    filterUserId,
    myBorrowedCount,
    filteredBooks,
    fetchBooks,
    toggleStatus,
    addBook,
    updateBook,
    deleteBook,
    startPolling,
    stopPolling,
  }
})
