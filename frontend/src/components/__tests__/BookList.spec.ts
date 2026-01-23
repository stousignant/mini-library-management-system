import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import BookList from '../BookList.vue'
import { useBookStore } from '@/stores/bookStore'
import { useStatsStore } from '@/stores/statsStore'
import { BookStatus } from '@/types/Book'

describe('BookList', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('displays loading state', () => {
    const wrapper = mount(BookList, {
      global: {
        plugins: [
          createTestingPinia({
            createSpy: vi.fn,
            initialState: {
              book: {
                isLoading: true,
                books: [],
                error: null,
              },
              stats: {
                total: 0,
                available: 0,
                borrowed: 0,
                isLoading: false,
                error: null,
              },
            },
          }),
        ],
      },
    })

    expect(wrapper.find('[data-testid="loading-state"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="book-list"]').exists()).toBe(false)
  })

  it('fetches books and stats on mount', () => {
    mount(BookList, {
      global: {
        plugins: [
          createTestingPinia({
            createSpy: vi.fn,
          }),
        ],
      },
    })

    const bookStore = useBookStore()
    const statsStore = useStatsStore()

    expect(bookStore.fetchBooks).toHaveBeenCalledOnce()
    expect(statsStore.fetchStatistics).toHaveBeenCalledOnce()
  })

  it('renders book list when books are loaded', () => {
    const mockBooks = [
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

    const wrapper = mount(BookList, {
      global: {
        plugins: [
          createTestingPinia({
            createSpy: vi.fn,
            initialState: {
              book: {
                isLoading: false,
                books: mockBooks,
                error: null,
              },
              stats: {
                total: 2,
                available: 1,
                borrowed: 1,
                isLoading: false,
                error: null,
              },
            },
          }),
        ],
      },
    })

    expect(wrapper.find('[data-testid="loading-state"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="book-list"]').exists()).toBe(true)

    const bookItems = wrapper.findAll('[data-testid^="book-item-"]')
    expect(bookItems).toHaveLength(2)

    expect(wrapper.text()).toContain('The Great Gatsby')
    expect(wrapper.text()).toContain('F. Scott Fitzgerald')
    expect(wrapper.text()).toContain('1984')
    expect(wrapper.text()).toContain('George Orwell')
  })

  it('displays error state', () => {
    const wrapper = mount(BookList, {
      global: {
        plugins: [
          createTestingPinia({
            createSpy: vi.fn,
            initialState: {
              book: {
                isLoading: false,
                books: [],
                error: 'Failed to fetch books',
              },
              stats: {
                total: 0,
                available: 0,
                borrowed: 0,
                isLoading: false,
                error: null,
              },
            },
          }),
        ],
      },
    })

    expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Failed to fetch books')
  })

  it('displays empty state when no books exist', () => {
    const wrapper = mount(BookList, {
      global: {
        plugins: [
          createTestingPinia({
            createSpy: vi.fn,
            initialState: {
              book: {
                isLoading: false,
                books: [],
                error: null,
              },
              stats: {
                total: 0,
                available: 0,
                borrowed: 0,
                isLoading: false,
                error: null,
              },
            },
          }),
        ],
      },
    })

    expect(wrapper.find('[data-testid="book-list"]').exists()).toBe(true)
    expect(wrapper.findAll('[data-testid^="book-item-"]')).toHaveLength(0)
  })

  it('displays stats dashboard with correct values', () => {
    const wrapper = mount(BookList, {
      global: {
        plugins: [
          createTestingPinia({
            createSpy: vi.fn,
            initialState: {
              book: {
                isLoading: false,
                books: [],
                error: null,
              },
              stats: {
                total: 10,
                available: 7,
                borrowed: 3,
                isLoading: false,
                error: null,
              },
            },
          }),
        ],
      },
    })

    expect(wrapper.text()).toContain('Total Books')
    expect(wrapper.text()).toContain('10')
    expect(wrapper.text()).toContain('Available')
    expect(wrapper.text()).toContain('7')
    expect(wrapper.text()).toContain('Borrowed')
    expect(wrapper.text()).toContain('3')
  })
})
