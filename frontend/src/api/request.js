import axios from 'axios'
import { getCurrentInstance } from 'vue'
import router from '@/router'

let authStore = null

const getAuthStore = () => {
  if (!authStore) {
    try {
      const instance = getCurrentInstance()
      if (instance) {
        const { useAuthStore } = require('@/stores/auth')
        authStore = useAuthStore()
      }
    } catch (e) {
      // store not ready
    }
  }
  return authStore
}

const request = axios.create({
  baseURL: '/api',
  timeout: 30000
})

request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/login')
    }
    return Promise.reject(error.response?.data || error)
  }
)

export default request