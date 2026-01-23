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

    expect(wrapper.text()).toContain('Sign In')
    const signInButton = wrapper.find('button')
    expect(signInButton.exists()).toBe(true)
  })

  it('shows user info when authenticated', async () => {
    const wrapper = mount(AuthButton)
    const authStore = useAuthStore()

    const mockUser: Partial<User> = {
      id: '123',
      email: 'test@example.com',
      app_metadata: { role: 'MEMBER' },
    }
    const mockSession: Partial<Session> = {
      access_token: 'test-token',
      user: mockUser as User,
    }

    authStore.session = mockSession as Session
    authStore.user = mockUser as User
    authStore.userRole = 'MEMBER'

    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('test@example.com')
    expect(wrapper.text()).toContain('Member')
    expect(wrapper.text()).toContain('Sign Out')
  })

  it('shows admin badge for admin users', async () => {
    const wrapper = mount(AuthButton)
    const authStore = useAuthStore()

    const mockUser: Partial<User> = {
      id: '123',
      email: 'admin@example.com',
      app_metadata: { role: 'ADMIN' },
    }
    const mockSession: Partial<Session> = {
      access_token: 'test-token',
      user: mockUser as User,
    }

    authStore.session = mockSession as Session
    authStore.user = mockUser as User
    authStore.userRole = 'ADMIN'

    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Admin')
    expect(wrapper.text()).toContain('admin@example.com')
  })

  it('calls signInWithGithub when GitHub button clicked in dialog', async () => {
    const wrapper = mount(AuthButton, {
      attachTo: document.body,
    })
    const authStore = useAuthStore()
    const signInSpy = vi
      .spyOn(authStore, 'signInWithGithub')
      .mockResolvedValue()

    const signInButton = wrapper.find('button')
    await signInButton.trigger('click')
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    const githubButton = document.querySelector('button:has(svg)')
    expect(githubButton).toBeTruthy()
    expect(githubButton?.textContent).toContain('GitHub')

    await githubButton?.dispatchEvent(new MouseEvent('click', { bubbles: true }))
    await wrapper.vm.$nextTick()

    expect(signInSpy).toHaveBeenCalled()
    wrapper.unmount()
  })

  it('calls signInWithGoogle when Google button clicked in dialog', async () => {
    const wrapper = mount(AuthButton, {
      attachTo: document.body,
    })
    const authStore = useAuthStore()
    const signInSpy = vi
      .spyOn(authStore, 'signInWithGoogle')
      .mockResolvedValue()

    const signInButton = wrapper.find('button')
    await signInButton.trigger('click')
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    const buttons = Array.from(document.querySelectorAll('button'))
    const googleButton = buttons.find(b => b.textContent?.includes('Google'))
    expect(googleButton).toBeTruthy()

    await googleButton?.dispatchEvent(new MouseEvent('click', { bubbles: true }))
    await wrapper.vm.$nextTick()

    expect(signInSpy).toHaveBeenCalled()
    wrapper.unmount()
  })

  it('calls signOut when sign out button clicked', async () => {
    const wrapper = mount(AuthButton)
    const authStore = useAuthStore()

    const mockUser: Partial<User> = {
      id: '123',
      email: 'test@example.com',
      app_metadata: { role: 'MEMBER' },
    }
    const mockSession: Partial<Session> = {
      access_token: 'test-token',
      user: mockUser as User,
    }

    authStore.session = mockSession as Session
    authStore.user = mockUser as User

    await wrapper.vm.$nextTick()

    const signOutSpy = vi.spyOn(authStore, 'signOut').mockResolvedValue()
    const buttons = wrapper.findAll('button')
    const signOutButton = buttons.find(b => b.text() === 'Sign Out')
    expect(signOutButton).toBeTruthy()

    await signOutButton!.trigger('click')

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
