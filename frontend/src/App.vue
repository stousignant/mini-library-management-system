<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { useTheme } from '@/composables/useTheme'
import AuthButton from './components/AuthButton.vue'
import BookList from './components/BookList.vue'
import { Moon, Sun } from 'lucide-vue-next'
import { Toaster } from 'vue-sonner'

const authStore = useAuthStore()
const { isDark, toggleTheme } = useTheme()

onMounted(async () => {
  await authStore.initialize()
})
</script>

<template>
  <div class="min-h-screen bg-background">
    <Toaster
      position="bottom-right"
      :duration="4500"
      :close-button="true"
      :rich-colors="true"
      :expand="false"
      :offset="16"
    />
    <header class="border-b bg-card">
      <div
        class="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center"
      >
        <h1 class="text-3xl font-bold text-foreground">
          Library Management System
        </h1>
        <div class="flex items-center gap-3">
          <button
            class="relative inline-flex items-center h-9 rounded-full border border-input bg-background p-1 hover:bg-accent transition-colors"
            :aria-label="
              isDark ? 'Switch to light mode' : 'Switch to dark mode'
            "
            @click="toggleTheme"
          >
            <div class="flex items-center gap-1 px-1">
              <div
                :class="[
                  'flex items-center justify-center w-7 h-7 rounded-full transition-all',
                  !isDark
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground',
                ]"
              >
                <Sun class="h-4 w-4" />
              </div>
              <div
                :class="[
                  'flex items-center justify-center w-7 h-7 rounded-full transition-all',
                  isDark
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground',
                ]"
              >
                <Moon class="h-4 w-4" />
              </div>
            </div>
          </button>
          <AuthButton />
        </div>
      </div>
    </header>
    <main class="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
      <div class="mb-6">
        <h2 class="text-2xl font-semibold text-foreground">Book Collection</h2>
        <p class="text-muted-foreground mt-1">
          Browse and manage your library books.
        </p>
      </div>
      <BookList />
    </main>
  </div>
</template>
