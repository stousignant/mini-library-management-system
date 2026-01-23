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

  const isAuthenticated = computed(() => !!session.value)

  const isAdmin = computed(() => userRole.value === 'ADMIN')

  async function fetchUserProfile() {
    try {
      const response = await apiClient.get('/profile')
      userRole.value = response.data.role
    } catch (error) {
      console.error('Error fetching user profile:', error)
      userRole.value = null
    }
  }

  async function initialize() {
    loading.value = true
    try {
      const { data: { session: currentSession }, error } = await supabase.auth.getSession()

      if (error) {
        console.error('Error getting session:', error)
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
        }
      })
    } catch (error) {
      console.error('Error initializing auth:', error)
    } finally {
      loading.value = false
    }
  }

  async function signInWithGithub() {
    loading.value = true
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'github',
      })

      if (error) {
        console.error('Error signing in:', error)
        throw error
      }
    } catch (error) {
      console.error('Error signing in with GitHub:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function signOut() {
    loading.value = true
    try {
      const { error } = await supabase.auth.signOut()

      if (error) {
        console.error('Error signing out:', error)
        throw error
      }

      session.value = null
      user.value = null
      userRole.value = null
    } catch (error) {
      console.error('Error signing out:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  return {
    user,
    session,
    loading,
    isAuthenticated,
    userRole,
    isAdmin,
    initialize,
    signInWithGithub,
    signOut,
  }
})
