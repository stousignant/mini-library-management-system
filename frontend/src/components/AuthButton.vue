<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Github, Loader2 } from 'lucide-vue-next'

const authStore = useAuthStore()
const isSignInDialogOpen = ref(false)

const handleSignInWithGithub = async () => {
  try {
    await authStore.signInWithGithub()
    isSignInDialogOpen.value = false
  } catch (error) {
    console.error('Sign in with GitHub failed:', error)
  }
}

const handleSignInWithGoogle = async () => {
  try {
    await authStore.signInWithGoogle()
    isSignInDialogOpen.value = false
  } catch (error) {
    console.error('Sign in with Google failed:', error)
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
    <div v-if="authStore.loading" class="flex items-center gap-2 text-muted-foreground">
      <Loader2 class="h-5 w-5 animate-spin" />
      <span class="text-sm">Loading...</span>
    </div>

    <!-- Authenticated State -->
    <div v-else-if="authStore.isAuthenticated" class="flex items-center gap-3">
      <div class="flex items-center gap-2">
        <span class="text-sm text-foreground">{{ authStore.user?.email }}</span>
        <Badge v-if="authStore.isAdmin" variant="default">
          Admin
        </Badge>
        <Badge v-else variant="secondary">
          Member
        </Badge>
      </div>
      <Button
        variant="outline"
        @click="handleSignOut"
      >
        Sign Out
      </Button>
    </div>

    <!-- Unauthenticated State -->
    <Dialog v-else v-model:open="isSignInDialogOpen">
      <DialogTrigger as-child>
        <Button variant="default">
          Sign In
        </Button>
      </DialogTrigger>
      <DialogContent class="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Sign in to Library Management System</DialogTitle>
        </DialogHeader>
        <div class="flex flex-col gap-3 py-4">
          <Button
            variant="default"
            class="w-full"
            @click="handleSignInWithGithub"
          >
            <Github class="mr-2 h-5 w-5" />
            Sign in with GitHub
          </Button>

          <Button
            variant="outline"
            class="w-full"
            @click="handleSignInWithGoogle"
          >
            <svg
              class="mr-2 w-5 h-5"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            Sign in with Google
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  </div>
</template>
