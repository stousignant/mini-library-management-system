import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getBookStatistics, type BookStatistics } from '@/services/api'
import { STATS_POLLING_INTERVAL_MS } from '@/constants/global'

export const useStatsStore = defineStore('stats', () => {
  const total = ref(0)
  const available = ref(0)
  const borrowed = ref(0)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  let pollingInterval: ReturnType<typeof setInterval> | null = null

  async function fetchStatistics() {
    isLoading.value = true
    error.value = null

    try {
      const stats: BookStatistics = await getBookStatistics()
      total.value = stats.total
      available.value = stats.available
      borrowed.value = stats.borrowed
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : 'Failed to fetch statistics'
      console.error('Failed to fetch book statistics:', err)
    } finally {
      isLoading.value = false
    }
  }

  function startPolling() {
    // Clear any existing polling interval
    stopPolling()

    // Set up new polling interval
    pollingInterval = setInterval(() => {
      fetchStatistics()
    }, STATS_POLLING_INTERVAL_MS)
  }

  function stopPolling() {
    if (pollingInterval) {
      clearInterval(pollingInterval)
      pollingInterval = null
    }
  }

  return {
    total,
    available,
    borrowed,
    isLoading,
    error,
    fetchStatistics,
    startPolling,
    stopPolling,
  }
})
