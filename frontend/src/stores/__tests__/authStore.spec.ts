import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../authStore'
import { supabase } from '@/services/supabase'
import apiClient from '@/services/api'
import type { User, Session } from '@supabase/supabase-js'

vi.mock('@/services/supabase', () => ({
    supabase: {
        auth: {
            getSession: vi.fn(),
            signInWithOAuth: vi.fn(),
            signOut: vi.fn(),
            onAuthStateChange: vi.fn(),
        },
    },
}))

vi.mock('@/services/api', () => ({
    default: {
        get: vi.fn(),
        post: vi.fn(),
        put: vi.fn(),
        delete: vi.fn(),
    },
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
            user: { id: '123', email: 'test@example.com' } as unknown as User,
        } as Session

        expect(authStore.isAuthenticated).toBe(true)
    })

    it('userRole extracts role from session user metadata', async () => {
        const authStore = useAuthStore()

        vi.mocked(supabase.auth.getSession).mockResolvedValue({
            data: {
                session: {
                    access_token: 'test-token',
                    user: {
                        id: '123',
                        email: 'admin@example.com',
                        app_metadata: { role: 'ADMIN' },
                    } as unknown as User,
                } as Session,
            },
            error: null,
        })

        vi.mocked(supabase.auth.onAuthStateChange).mockReturnValue({
            data: { subscription: { unsubscribe: vi.fn() } },
        } as any)

        vi.mocked(apiClient.get).mockResolvedValue({
            data: { role: 'ADMIN' },
        })

        await authStore.initialize()

        expect(authStore.userRole).toBe('ADMIN')
    })

    it('isAdmin returns true for ADMIN role', async () => {
        const authStore = useAuthStore()

        vi.mocked(supabase.auth.getSession).mockResolvedValue({
            data: {
                session: {
                    access_token: 'test-token',
                    user: {
                        id: '123',
                        email: 'admin@example.com',
                        app_metadata: { role: 'ADMIN' },
                    } as unknown as User,
                } as Session,
            },
            error: null,
        })

        vi.mocked(supabase.auth.onAuthStateChange).mockReturnValue({
            data: { subscription: { unsubscribe: vi.fn() } },
        } as any)

        vi.mocked(apiClient.get).mockResolvedValue({
            data: { role: 'ADMIN' },
        })

        await authStore.initialize()

        expect(authStore.isAdmin).toBe(true)
    })

    it('isAdmin returns false for MEMBER role', async () => {
        const authStore = useAuthStore()

        vi.mocked(supabase.auth.getSession).mockResolvedValue({
            data: {
                session: {
                    access_token: 'test-token',
                    user: {
                        id: '123',
                        email: 'member@example.com',
                        app_metadata: { role: 'MEMBER' },
                    } as unknown as User,
                } as Session,
            },
            error: null,
        })

        vi.mocked(supabase.auth.onAuthStateChange).mockReturnValue({
            data: { subscription: { unsubscribe: vi.fn() } },
        } as any)

        vi.mocked(apiClient.get).mockResolvedValue({
            data: { role: 'MEMBER' },
        })

        await authStore.initialize()

        expect(authStore.isAdmin).toBe(false)
    })

    it('signInWithGithub calls Supabase OAuth', async () => {
        const authStore = useAuthStore()

        vi.mocked(supabase.auth.signInWithOAuth).mockResolvedValue({
            data: { provider: 'github', url: 'https://github.com/login' },
            error: null,
        })

        await authStore.signInWithGithub()

        expect(supabase.auth.signInWithOAuth).toHaveBeenCalledWith({
            provider: 'github',
        })
    })

    it('signInWithGoogle calls Supabase OAuth', async () => {
        const authStore = useAuthStore()

        vi.mocked(supabase.auth.signInWithOAuth).mockResolvedValue({
            data: { provider: 'google', url: 'https://accounts.google.com/signin' },
            error: null,
        })

        await authStore.signInWithGoogle()

        expect(supabase.auth.signInWithOAuth).toHaveBeenCalledWith({
            provider: 'google',
        })
    })

    it('signOut clears session and user', async () => {
        const authStore = useAuthStore()

        authStore.session = {
            access_token: 'test-token',
            user: { id: '123', email: 'test@example.com' } as unknown as User,
        } as Session
        authStore.user = { id: '123', email: 'test@example.com' } as unknown as User

        vi.mocked(supabase.auth.signOut).mockResolvedValue({
            error: null,
        })

        await authStore.signOut()

        expect(supabase.auth.signOut).toHaveBeenCalled()
        expect(authStore.session).toBeNull()
        expect(authStore.user).toBeNull()
    })

    it('initialize loads existing session', async () => {
        const authStore = useAuthStore()

        vi.mocked(supabase.auth.getSession).mockResolvedValue({
            data: {
                session: {
                    access_token: 'test-token',
                    user: {
                        id: '123',
                        email: 'test@example.com',
                        app_metadata: { role: 'MEMBER' },
                    } as unknown as User,
                } as Session,
            },
            error: null,
        })

        vi.mocked(supabase.auth.onAuthStateChange).mockReturnValue({
            data: { subscription: { unsubscribe: vi.fn() } },
        } as any)

        vi.mocked(apiClient.get).mockResolvedValue({
            data: { role: 'MEMBER' },
        })

        await authStore.initialize()

        expect(authStore.session).not.toBeNull()
        expect(authStore.user).not.toBeNull()
        expect(authStore.user?.email).toBe('test@example.com')
    })
})
