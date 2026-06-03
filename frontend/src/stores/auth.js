import { defineStore } from 'pinia'
import { login as apiLogin, getCurrentUser, changePassword as apiChangePassword } from '@/api/auth'
import router from '@/router'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null')
  }),

  actions: {
    async login(username, password) {
      const res = await apiLogin({ username, password })
      this.token = res.access_token
      this.user = res.user
      localStorage.setItem('token', this.token)
      localStorage.setItem('user', JSON.stringify(this.user))
      router.push('/dashboard')
      return res
    },

    async fetchUser() {
      if (!this.token) return null
      try {
        this.user = await getCurrentUser()
        localStorage.setItem('user', JSON.stringify(this.user))
        return this.user
      } catch (e) {
        this.logout()
        return null
      }
    },

    async changePassword(oldPassword, newPassword) {
      return await apiChangePassword({ old_password: oldPassword, new_password: newPassword })
    },

    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/login')
    },

    hasRole(code) {
      if (!this.user?.roles) return false
      return this.user.roles.some(r => r.code === code)
    },

    hasPermission(code) {
      if (!this.user?.roles) return false
      for (const role of this.user.roles) {
        if (role.permissions?.some(p => p.code === code)) {
          return true
        }
      }
      return false
    }
  }
})