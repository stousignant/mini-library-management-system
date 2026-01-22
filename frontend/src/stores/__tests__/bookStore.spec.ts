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

    expect(apiClient.get).toHaveBeenCalledWith('/books/')
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

  describe('search functionality', () => {
    it('filters books by title (case-insensitive)', () => {
      const store = useBookStore()

      store.books = [
        {
          id: 1,
          title: 'Dune',
          author: 'Frank Herbert',
          isbn: '9780441172719',
          status: BookStatus.Available,
          created_at: '2024-01-01T00:00:00Z'
        },
        {
          id: 2,
          title: 'Harry Potter',
          author: 'J.K. Rowling',
          isbn: '9780439708180',
          status: BookStatus.Available,
          created_at: '2024-01-02T00:00:00Z'
        },
        {
          id: 3,
          title: 'Domain Driven Design',
          author: 'Eric Evans',
          isbn: '9780321125217',
          status: BookStatus.Available,
          created_at: '2024-01-03T00:00:00Z'
        }
      ]

      store.searchQuery = 'dune'
      expect(store.filteredBooks).toHaveLength(1)
      expect(store.filteredBooks[0].title).toBe('Dune')
    })

    it('filters books by author', () => {
      const store = useBookStore()

      store.books = [
        {
          id: 1,
          title: 'Dune',
          author: 'Frank Herbert',
          isbn: '9780441172719',
          status: BookStatus.Available,
          created_at: '2024-01-01T00:00:00Z'
        },
        {
          id: 2,
          title: 'Harry Potter',
          author: 'J.K. Rowling',
          isbn: '9780439708180',
          status: BookStatus.Available,
          created_at: '2024-01-02T00:00:00Z'
        }
      ]

      store.searchQuery = 'rowling'
      expect(store.filteredBooks).toHaveLength(1)
      expect(store.filteredBooks[0].author).toBe('J.K. Rowling')
    })

    it('filters books by partial match', () => {
      const store = useBookStore()

      store.books = [
        {
          id: 1,
          title: 'Domain Driven Design',
          author: 'Eric Evans',
          isbn: '9780321125217',
          status: BookStatus.Available,
          created_at: '2024-01-01T00:00:00Z'
        },
        {
          id: 2,
          title: 'The Great Gatsby',
          author: 'F. Scott Fitzgerald',
          isbn: '9780743273565',
          status: BookStatus.Available,
          created_at: '2024-01-02T00:00:00Z'
        }
      ]

      store.searchQuery = 'Design'
      expect(store.filteredBooks).toHaveLength(1)
      expect(store.filteredBooks[0].title).toBe('Domain Driven Design')
    })

    it('returns all books when searchQuery is empty', () => {
      const store = useBookStore()

      store.books = [
        {
          id: 1,
          title: 'Book 1',
          author: 'Author 1',
          isbn: '1111111111',
          status: BookStatus.Available,
          created_at: '2024-01-01T00:00:00Z'
        },
        {
          id: 2,
          title: 'Book 2',
          author: 'Author 2',
          isbn: '2222222222',
          status: BookStatus.Available,
          created_at: '2024-01-02T00:00:00Z'
        }
      ]

      store.searchQuery = ''
      expect(store.filteredBooks).toHaveLength(2)
      expect(store.filteredBooks).toEqual(store.books)
    })
  })
})
