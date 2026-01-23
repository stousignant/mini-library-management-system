import { ref, watch, onMounted } from 'vue'

const THEME_STORAGE_KEY = 'library-theme'

const isDark = ref(false)

export function useTheme() {
  const toggleTheme = () => {
    isDark.value = !isDark.value
  }

  const setTheme = (dark: boolean) => {
    isDark.value = dark
  }

  const initializeTheme = () => {
    const stored = localStorage.getItem(THEME_STORAGE_KEY)
    if (stored) {
      isDark.value = stored === 'dark'
    } else {
      isDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches
    }
  }

  watch(
    isDark,
    dark => {
      const html = document.documentElement
      if (dark) {
        html.classList.add('dark')
        localStorage.setItem(THEME_STORAGE_KEY, 'dark')
      } else {
        html.classList.remove('dark')
        localStorage.setItem(THEME_STORAGE_KEY, 'light')
      }
    },
    { immediate: true }
  )

  onMounted(() => {
    initializeTheme()
  })

  return {
    isDark,
    toggleTheme,
    setTheme,
  }
}
