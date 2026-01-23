import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../authStore'

const mockSupabase = {
  auth: {
    getSession: vi.fn(),
    signInWithOAuth: vi.fn(),
    signOut: vi.fn(),
    onAuthStateChange: vi.fn(),
  },
}

vi.mock('@/services/supabase', () => ({
  supabase: mockSupabase,
}))

describe('authStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('initializes with null user and session', () => {
    const authStore = useAuthStore()

    expect(authStore.user).toBeNull()
    expect(authStore.session).toBeNull()
    expect(authStore.loading).toBe(false)
  })

  it('isAuthenticated returns false when no session', () => {
    const authStore = useAuthStore()

    expect(authStore.isAuthenticated).toBe(false)
  })

  it('isAuthenticated returns true when session exists', () => {
    const authStore = useAuthStore()
    authStore.session = {
      access_token: 'test-token',
      user: { id: '123', email: 'test@example.com' },
    } as any

    expect(authStore.isAuthenticated).toBe(true)
  })

  it('userRole extracts role from session user metadata', async () => {
    const authStore = useAuthStore()

    mockSupabase.auth.getSession.mockResolvedValue({
      data: {
        session: {
          access_token: 'test-token',
          user: {
            id: '123',
            email: 'admin@example.com',
            app_metadata: { role: 'ADMIN' },
          },
        },
      },
      error: null,
    })

    await authStore.initialize()

    expect(authStore.userRole).toBe('ADMIN')
  })

  it('isAdmin returns true for ADMIN role', async () => {
    const authStore = useAuthStore()

    mockSupabase.auth.getSession.mockResolvedValue({
      data: {
        session: {
          access_token: 'test-token',
          user: {
            id: '123',
            email: 'admin@example.com',
            app_metadata: { role: 'ADMIN' },
          },
        },
      },
      error: null,
    })

    await authStore.initialize()

    expect(authStore.isAdmin).toBe(true)
  })

  it('isAdmin returns false for MEMBER role', async () => {
    const authStore = useAuthStore()

    mockSupabase.auth.getSession.mockResolvedValue({
      data: {
        session: {
          access_token: 'test-token',
          user: {
            id: '123',
            email: 'member@example.com',
            app_metadata: { role: 'MEMBER' },
          },
        },
      },
      error: null,
    })

    await authStore.initialize()

    expect(authStore.isAdmin).toBe(false)
  })

  it('signInWithGithub calls Supabase OAuth', async () => {
    const authStore = useAuthStore()

    mockSupabase.auth.signInWithOAuth.mockResolvedValue({
      data: { provider: 'github', url: 'https://github.com/login' },
      error: null,
    })

    await authStore.signInWithGithub()

    expect(mockSupabase.auth.signInWithOAuth).toHaveBeenCalledWith({
      provider: 'github',
    })
  })

  it('signInWithGoogle calls Supabase OAuth', async () => {
    const authStore = useAuthStore()

    mockSupabase.auth.signInWithOAuth.mockResolvedValue({
      data: { provider: 'google', url: 'https://accounts.google.com/signin' },
      error: null,
    })

    await authStore.signInWithGoogle()

    expect(mockSupabase.auth.signInWithOAuth).toHaveBeenCalledWith({
      provider: 'google',
    })
  })

  it('signOut clears session and user', async () => {
    const authStore = useAuthStore()

    authStore.session = {
      access_token: 'test-token',
      user: { id: '123', email: 'test@example.com' },
    } as any
    authStore.user = { id: '123', email: 'test@example.com' } as any

    mockSupabase.auth.signOut.mockResolvedValue({
      error: null,
    })

    await authStore.signOut()

    expect(mockSupabase.auth.signOut).toHaveBeenCalled()
    expect(authStore.session).toBeNull()
    expect(authStore.user).toBeNull()
  })

  it('initialize loads existing session', async () => {
    const authStore = useAuthStore()

    mockSupabase.auth.getSession.mockResolvedValue({
      data: {
        session: {
          access_token: 'test-token',
          user: {
            id: '123',
            email: 'test@example.com',
            app_metadata: { role: 'MEMBER' },
          },
        },
      },
      error: null,
    })

    mockSupabase.auth.onAuthStateChange.mockReturnValue({
      data: { subscription: { unsubscribe: vi.fn() } },
    })

    await authStore.initialize()

    expect(authStore.session).not.toBeNull()
    expect(authStore.user).not.toBeNull()
    expect(authStore.user?.email).toBe('test@example.com')
  })
})
