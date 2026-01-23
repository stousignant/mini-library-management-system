<script setup lang="ts">
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()

const handleSignIn = async () => {
  try {
    await authStore.signInWithGithub()
  } catch (error) {
    console.error('Sign in failed:', error)
  }
}

const handleSignOut = async () => {
  try {
    await authStore.signOut()
  } catch (error) {
    console.error('Sign out failed:', error)
  }
}
</script>

<template>
  <div class="flex items-center gap-3">
    <!-- Loading State -->
    <div v-if="authStore.loading" class="flex items-center gap-2 text-gray-600">
      <svg
        class="animate-spin h-5 w-5"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          class="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          stroke-width="4"
        ></circle>
        <path
          class="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        ></path>
      </svg>
      <span class="text-sm">Loading...</span>
    </div>

    <!-- Authenticated State -->
    <div v-else-if="authStore.isAuthenticated" class="flex items-center gap-3">
      <div class="flex items-center gap-2">
        <span class="text-sm text-gray-700">{{ authStore.user?.email }}</span>
        <span
          v-if="authStore.isAdmin"
          class="px-2 py-1 text-xs font-semibold text-white bg-purple-600 rounded-full"
        >
          Admin
        </span>
        <span
          v-else
          class="px-2 py-1 text-xs font-semibold text-gray-700 bg-gray-200 rounded-full"
        >
          Member
        </span>
      </div>
      <button
        @click="handleSignOut"
        class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
      >
        Sign Out
      </button>
    </div>

    <!-- Unauthenticated State -->
    <button
      v-else
      @click="handleSignIn"
      class="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-gray-900 rounded-md hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-900 transition-colors"
    >
      <svg
        class="w-5 h-5"
        fill="currentColor"
        viewBox="0 0 20 20"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          fill-rule="evenodd"
          d="M10 0C4.477 0 0 4.477 0 10c0 4.42 2.865 8.17 6.839 9.49.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.463-1.11-1.463-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0110 4.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C17.137 18.165 20 14.418 20 10c0-5.523-4.477-10-10-10z"
          clip-rule="evenodd"
        />
      </svg>
      Sign in with GitHub
    </button>
  </div>
</template>
