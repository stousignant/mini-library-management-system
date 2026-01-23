import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { supabase } from '@/services/supabase'
import type { User, Session } from '@supabase/supabase-js'
import apiClient from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const session = ref<Session | null>(null)
  const loading = ref(false)
  const userRole = ref<string | null>(null)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!session.value)

  const isAdmin = computed(() => userRole.value === 'ADMIN')

  async function fetchUserProfile() {
    try {
      const response = await apiClient.get('/profile')
      userRole.value = response.data.role
      error.value = null
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch user profile'
      console.error('Error fetching user profile:', errorMessage)
      error.value = errorMessage
      userRole.value = null
    }
  }

  async function initialize() {
    loading.value = true
    error.value = null
    try {
      const { data: { session: currentSession }, error: sessionError } = await supabase.auth.getSession()

      if (sessionError) {
        error.value = sessionError.message
        console.error('Error getting session:', sessionError)
        return
      }

      if (currentSession) {
        session.value = currentSession
        user.value = currentSession.user
        await fetchUserProfile()
      }

      supabase.auth.onAuthStateChange(async (_event, newSession) => {
        session.value = newSession
        user.value = newSession?.user ?? null

        if (newSession) {
          await fetchUserProfile()
        } else {
          userRole.value = null
          error.value = null
        }
      })
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to initialize authentication'
      error.value = errorMessage
      console.error('Error initializing auth:', errorMessage)
    } finally {
      loading.value = false
    }
  }

  async function signInWithGithub() {
    loading.value = true
    error.value = null
    try {
      const { error: authError } = await supabase.auth.signInWithOAuth({
        provider: 'github',
      })

      if (authError) {
        error.value = authError.message
        console.error('Error signing in:', authError)
        throw authError
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to sign in with GitHub'
      error.value = errorMessage
      console.error('Error signing in with GitHub:', errorMessage)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function signOut() {
    loading.value = true
    error.value = null
    try {
      const { error: authError } = await supabase.auth.signOut()

      if (authError) {
        error.value = authError.message
        console.error('Error signing out:', authError)
        throw authError
      }

      session.value = null
      user.value = null
      userRole.value = null
      error.value = null
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to sign out'
      error.value = errorMessage
      console.error('Error signing out:', errorMessage)
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    user,
    session,
    loading,
    error,
    isAuthenticated,
    userRole,
    isAdmin,
    initialize,
    signInWithGithub,
    signOut,
  }
})
