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
        created_at: '2024-01-01T00:00:00Z',
      },
      {
        id: 2,
        title: '1984',
        author: 'George Orwell',
        isbn: '9780451524935',
        status: BookStatus.Borrowed,
        created_at: '2024-01-02T00:00:00Z',
      },
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
          created_at: '2024-01-01T00:00:00Z',
        },
        {
          id: 2,
          title: 'Harry Potter',
          author: 'J.K. Rowling',
          isbn: '9780439708180',
          status: BookStatus.Available,
          created_at: '2024-01-02T00:00:00Z',
        },
        {
          id: 3,
          title: 'Domain Driven Design',
          author: 'Eric Evans',
          isbn: '9780321125217',
          status: BookStatus.Available,
          created_at: '2024-01-03T00:00:00Z',
        },
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
          created_at: '2024-01-01T00:00:00Z',
        },
        {
          id: 2,
          title: 'Harry Potter',
          author: 'J.K. Rowling',
          isbn: '9780439708180',
          status: BookStatus.Available,
          created_at: '2024-01-02T00:00:00Z',
        },
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
          created_at: '2024-01-01T00:00:00Z',
        },
        {
          id: 2,
          title: 'The Great Gatsby',
          author: 'F. Scott Fitzgerald',
          isbn: '9780743273565',
          status: BookStatus.Available,
          created_at: '2024-01-02T00:00:00Z',
        },
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
          created_at: '2024-01-01T00:00:00Z',
        },
        {
          id: 2,
          title: 'Book 2',
          author: 'Author 2',
          isbn: '2222222222',
          status: BookStatus.Available,
          created_at: '2024-01-02T00:00:00Z',
        },
      ]

      store.searchQuery = ''
      expect(store.filteredBooks).toHaveLength(2)
      expect(store.filteredBooks).toEqual(store.books)
    })
  })

  describe('toggleStatus', () => {
    it('toggles book from AVAILABLE to BORROWED', async () => {
      const store = useBookStore()

      store.books = [
        {
          id: 1,
          title: 'Test Book',
          author: 'Test Author',
          isbn: '1234567890',
          status: BookStatus.Available,
          created_at: '2024-01-01T00:00:00Z',
        },
      ]

      vi.mocked(apiClient.put).mockResolvedValueOnce({ data: {} })

      await store.toggleStatus(1)

      expect(apiClient.put).toHaveBeenCalledWith('/books/1', {
        status: BookStatus.Borrowed,
      })
      expect(store.books[0].status).toBe(BookStatus.Borrowed)
      expect(store.error).toBeNull()
    })

    it('toggles book from BORROWED to AVAILABLE', async () => {
      const store = useBookStore()

      store.books = [
        {
          id: 1,
          title: 'Test Book',
          author: 'Test Author',
          isbn: '1234567890',
          status: BookStatus.Borrowed,
          created_at: '2024-01-01T00:00:00Z',
        },
      ]

      vi.mocked(apiClient.put).mockResolvedValueOnce({ data: {} })

      await store.toggleStatus(1)

      expect(apiClient.put).toHaveBeenCalledWith('/books/1', {
        status: BookStatus.Available,
      })
      expect(store.books[0].status).toBe(BookStatus.Available)
      expect(store.error).toBeNull()
    })

    it('reverts status on API failure', async () => {
      const store = useBookStore()

      store.books = [
        {
          id: 1,
          title: 'Test Book',
          author: 'Test Author',
          isbn: '1234567890',
          status: BookStatus.Available,
          created_at: '2024-01-01T00:00:00Z',
        },
      ]

      vi.mocked(apiClient.put).mockRejectedValueOnce(new Error('Network error'))

      await store.toggleStatus(1)

      expect(store.books[0].status).toBe(BookStatus.Available)
      expect(store.error).toBe('Failed to update book status')
    })
  })

  describe('CRUD operations', () => {
    it('addBook creates new book via POST', async () => {
      const store = useBookStore()

      const newBook: Book = {
        id: 1,
        title: 'New Book',
        author: 'New Author',
        isbn: '1234567890',
        status: BookStatus.Available,
        created_at: '2024-01-01T00:00:00Z',
      }

      vi.mocked(apiClient.post).mockResolvedValueOnce({ data: newBook })

      await store.addBook({
        title: 'New Book',
        author: 'New Author',
        isbn: '1234567890',
      })

      expect(apiClient.post).toHaveBeenCalledWith('/books/', {
        title: 'New Book',
        author: 'New Author',
        isbn: '1234567890',
      })
      expect(store.books).toHaveLength(1)
      expect(store.books[0]).toEqual(newBook)
      expect(store.error).toBeNull()
    })

    it('addBook handles API errors', async () => {
      const store = useBookStore()

      vi.mocked(apiClient.post).mockRejectedValueOnce(
        new Error('Network error')
      )

      await expect(
        store.addBook({
          title: 'New Book',
          author: 'New Author',
        })
      ).rejects.toThrow()

      expect(store.error).toBe('Failed to create book')
      expect(store.books).toHaveLength(0)
    })

    it('updateBook updates existing book via PUT', async () => {
      const store = useBookStore()

      store.books = [
        {
          id: 1,
          title: 'Old Title',
          author: 'Old Author',
          isbn: '1234567890',
          status: BookStatus.Available,
          created_at: '2024-01-01T00:00:00Z',
        },
      ]

      const updatedBook: Book = {
        id: 1,
        title: 'Updated Title',
        author: 'Old Author',
        isbn: '1234567890',
        status: BookStatus.Available,
        created_at: '2024-01-01T00:00:00Z',
      }

      vi.mocked(apiClient.put).mockResolvedValueOnce({ data: updatedBook })

      await store.updateBook(1, { title: 'Updated Title' })

      expect(apiClient.put).toHaveBeenCalledWith('/books/1', {
        title: 'Updated Title',
      })
      expect(store.books[0].title).toBe('Updated Title')
      expect(store.error).toBeNull()
    })

    it('updateBook handles API errors', async () => {
      const store = useBookStore()

      store.books = [
        {
          id: 1,
          title: 'Test Book',
          author: 'Test Author',
          isbn: '1234567890',
          status: BookStatus.Available,
          created_at: '2024-01-01T00:00:00Z',
        },
      ]

      vi.mocked(apiClient.put).mockRejectedValueOnce(new Error('Network error'))

      await expect(
        store.updateBook(1, { title: 'Updated Title' })
      ).rejects.toThrow()

      expect(store.error).toBe('Failed to update book')
    })

    it('deleteBook removes book via DELETE', async () => {
      const store = useBookStore()

      store.books = [
        {
          id: 1,
          title: 'Book to Delete',
          author: 'Test Author',
          isbn: '1234567890',
          status: BookStatus.Available,
          created_at: '2024-01-01T00:00:00Z',
        },
        {
          id: 2,
          title: 'Book to Keep',
          author: 'Test Author',
          isbn: '0987654321',
          status: BookStatus.Available,
          created_at: '2024-01-02T00:00:00Z',
        },
      ]

      vi.mocked(apiClient.delete).mockResolvedValueOnce({ data: null })

      await store.deleteBook(1)

      expect(apiClient.delete).toHaveBeenCalledWith('/books/1')
      expect(store.books).toHaveLength(1)
      expect(store.books[0].id).toBe(2)
      expect(store.error).toBeNull()
    })

    it('deleteBook handles API errors', async () => {
      const store = useBookStore()

      store.books = [
        {
          id: 1,
          title: 'Test Book',
          author: 'Test Author',
          isbn: '1234567890',
          status: BookStatus.Available,
          created_at: '2024-01-01T00:00:00Z',
        },
      ]

      vi.mocked(apiClient.delete).mockRejectedValueOnce(
        new Error('Network error')
      )

      await expect(store.deleteBook(1)).rejects.toThrow()

      expect(store.error).toBe('Failed to delete book')
      expect(store.books).toHaveLength(1)
    })
  })
})
