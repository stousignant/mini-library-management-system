import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AuthButton from '../AuthButton.vue'
import { useAuthStore } from '@/stores/authStore'
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

describe('AuthButton', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('shows sign in button when not authenticated', () => {
    const wrapper = mount(AuthButton)

    expect(wrapper.text()).toContain('Sign in with GitHub')
    expect(wrapper.text()).toContain('Sign in with Google')
    expect(wrapper.findAll('button').length).toBeGreaterThanOrEqual(2)
  })

  it('shows user info when authenticated', async () => {
    const wrapper = mount(AuthButton)
    const authStore = useAuthStore()

    authStore.session = {
      access_token: 'test-token',
      user: {
        id: '123',
        email: 'test@example.com',
        app_metadata: { role: 'MEMBER' },
      } as unknown as User,
    } as Session
    authStore.user = {
      id: '123',
      email: 'test@example.com',
      app_metadata: { role: 'MEMBER' },
    } as unknown as User
    authStore.userRole = 'MEMBER'

    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('test@example.com')
    expect(wrapper.text()).toContain('Member')
    expect(wrapper.text()).toContain('Sign Out')
  })

  it('shows admin badge for admin users', async () => {
    const wrapper = mount(AuthButton)
    const authStore = useAuthStore()

    authStore.session = {
      access_token: 'test-token',
      user: {
        id: '123',
        email: 'admin@example.com',
        app_metadata: { role: 'ADMIN' },
      } as unknown as User,
    } as Session
    authStore.user = {
      id: '123',
      email: 'admin@example.com',
      app_metadata: { role: 'ADMIN' },
    } as unknown as User
    authStore.userRole = 'ADMIN'

    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Admin')
    expect(wrapper.find('.bg-purple-600').exists()).toBe(true)
  })

  it('calls signInWithGithub when GitHub button clicked', async () => {
    const wrapper = mount(AuthButton)
    const authStore = useAuthStore()
    const signInSpy = vi
      .spyOn(authStore, 'signInWithGithub')
      .mockResolvedValue()

    const buttons = wrapper.findAll('button')
    const githubButton = buttons.find(b => b.text().includes('GitHub'))
    await githubButton?.trigger('click')

    expect(signInSpy).toHaveBeenCalled()
  })

  it('calls signInWithGoogle when Google button clicked', async () => {
    const wrapper = mount(AuthButton)
    const authStore = useAuthStore()
    const signInSpy = vi
      .spyOn(authStore, 'signInWithGoogle')
      .mockResolvedValue()

    const buttons = wrapper.findAll('button')
    const googleButton = buttons.find(b => b.text().includes('Google'))
    await googleButton?.trigger('click')

    expect(signInSpy).toHaveBeenCalled()
  })

  it('calls signOut when sign out button clicked', async () => {
    const wrapper = mount(AuthButton)
    const authStore = useAuthStore()

    authStore.session = {
      access_token: 'test-token',
      user: {
        id: '123',
        email: 'test@example.com',
        app_metadata: { role: 'MEMBER' },
      } as unknown as User,
    } as Session
    authStore.user = {
      id: '123',
      email: 'test@example.com',
      app_metadata: { role: 'MEMBER' },
    } as unknown as User

    await wrapper.vm.$nextTick()

    const signOutSpy = vi.spyOn(authStore, 'signOut').mockResolvedValue()
    const buttons = wrapper.findAll('button')
    const signOutButton = buttons.find(b => b.text() === 'Sign Out')

    await signOutButton?.trigger('click')

    expect(signOutSpy).toHaveBeenCalled()
  })

  it('shows loading state', async () => {
    const wrapper = mount(AuthButton)
    const authStore = useAuthStore()

    authStore.loading = true
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Loading...')
    expect(wrapper.find('.animate-spin').exists()).toBe(true)
  })
})
