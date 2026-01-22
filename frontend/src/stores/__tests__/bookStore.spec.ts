import { setActivePinia, createPinia } from 'pinia'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useBookStore } from '../bookStore'
import apiClient from '@/services/api'
import type { Book } from '@/types/Book'
import { BookStatus } from '@/types/Book'

vi.mock('@/services/api')

describe('bookStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('fetches books successfully', async () => {
    const mockBooks: Book[] = [
      {
        id: 1,
        title: 'The Great Gatsby',
        author: 'F. Scott Fitzgerald',
        isbn: '9780743273565',
        status: BookStatus.Available,
        created_at: '2024-01-01T00:00:00Z'
      },
      {
        id: 2,
        title: '1984',
        author: 'George Orwell',
        isbn: '9780451524935',
        status: BookStatus.Borrowed,
        created_at: '2024-01-02T00:00:00Z'
      }
    ]

    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockBooks })

    const store = useBookStore()

    expect(store.isLoading).toBe(false)
    expect(store.books).toEqual([])

    const promise = store.fetchBooks()

    expect(store.isLoading).toBe(true)

    await promise

    expect(apiClient.get).toHaveBeenCalledWith('/books')
    expect(store.books).toEqual(mockBooks)
    expect(store.isLoading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('handles fetch errors', async () => {
    const errorMessage = 'Network error'
    vi.mocked(apiClient.get).mockRejectedValueOnce(new Error(errorMessage))

    const store = useBookStore()

    await store.fetchBooks()

    expect(store.books).toEqual([])
    expect(store.isLoading).toBe(false)
    expect(store.error).toBe('Failed to fetch books')
  })

  it('sets loading to false even when error occurs', async () => {
    vi.mocked(apiClient.get).mockRejectedValueOnce(new Error('Network error'))

    const store = useBookStore()

    await store.fetchBooks()

    expect(store.isLoading).toBe(false)
  })
})
