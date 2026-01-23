import { setActivePinia, createPinia } from 'pinia'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useStatsStore } from '../statsStore'
import * as api from '@/services/api'

vi.mock('@/services/api', () => ({
  getBookStatistics: vi.fn(),
}))

describe('statsStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('initializes with default values', () => {
    const store = useStatsStore()

    expect(store.total).toBe(0)
    expect(store.available).toBe(0)
    expect(store.borrowed).toBe(0)
    expect(store.isLoading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('fetches statistics successfully', async () => {
    const mockStats = {
      total: 10,
      available: 7,
      borrowed: 3,
    }

    vi.mocked(api.getBookStatistics).mockResolvedValueOnce(mockStats)

    const store = useStatsStore()

    expect(store.isLoading).toBe(false)

    const promise = store.fetchStatistics()

    expect(store.isLoading).toBe(true)

    await promise

    expect(api.getBookStatistics).toHaveBeenCalledOnce()
    expect(store.total).toBe(10)
    expect(store.available).toBe(7)
    expect(store.borrowed).toBe(3)
    expect(store.isLoading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('handles fetch errors gracefully', async () => {
    const errorMessage = 'Network error'
    vi.mocked(api.getBookStatistics).mockRejectedValueOnce(
      new Error(errorMessage)
    )

    const store = useStatsStore()

    await store.fetchStatistics()

    expect(store.total).toBe(0)
    expect(store.available).toBe(0)
    expect(store.borrowed).toBe(0)
    expect(store.isLoading).toBe(false)
    expect(store.error).toBe('Network error')
  })

  it('sets loading to false even when error occurs', async () => {
    vi.mocked(api.getBookStatistics).mockRejectedValueOnce(
      new Error('Network error')
    )

    const store = useStatsStore()

    await store.fetchStatistics()

    expect(store.isLoading).toBe(false)
  })

  it('updates statistics when fetched multiple times', async () => {
    const mockStats1 = {
      total: 5,
      available: 3,
      borrowed: 2,
    }

    const mockStats2 = {
      total: 10,
      available: 6,
      borrowed: 4,
    }

    vi.mocked(api.getBookStatistics)
      .mockResolvedValueOnce(mockStats1)
      .mockResolvedValueOnce(mockStats2)

    const store = useStatsStore()

    await store.fetchStatistics()
    expect(store.total).toBe(5)
    expect(store.available).toBe(3)
    expect(store.borrowed).toBe(2)

    await store.fetchStatistics()
    expect(store.total).toBe(10)
    expect(store.available).toBe(6)
    expect(store.borrowed).toBe(4)
  })

  it('clears error when fetch succeeds after a previous error', async () => {
    vi.mocked(api.getBookStatistics).mockRejectedValueOnce(
      new Error('Network error')
    )

    const store = useStatsStore()

    await store.fetchStatistics()
    expect(store.error).toBe('Network error')

    const mockStats = {
      total: 5,
      available: 3,
      borrowed: 2,
    }
    vi.mocked(api.getBookStatistics).mockResolvedValueOnce(mockStats)

    await store.fetchStatistics()
    expect(store.error).toBeNull()
    expect(store.total).toBe(5)
  })

  it('handles zero statistics correctly', async () => {
    const mockStats = {
      total: 0,
      available: 0,
      borrowed: 0,
    }

    vi.mocked(api.getBookStatistics).mockResolvedValueOnce(mockStats)

    const store = useStatsStore()

    await store.fetchStatistics()

    expect(store.total).toBe(0)
    expect(store.available).toBe(0)
    expect(store.borrowed).toBe(0)
    expect(store.error).toBeNull()
  })

  it('does not set statistics when request fails', async () => {
    const mockStats = {
      total: 5,
      available: 3,
      borrowed: 2,
    }

    vi.mocked(api.getBookStatistics).mockResolvedValueOnce(mockStats)

    const store = useStatsStore()

    await store.fetchStatistics()
    expect(store.total).toBe(5)

    vi.mocked(api.getBookStatistics).mockRejectedValueOnce(
      new Error('Network error')
    )
    await store.fetchStatistics()

    expect(store.total).toBe(5)
    expect(store.available).toBe(3)
    expect(store.borrowed).toBe(2)
  })
})
