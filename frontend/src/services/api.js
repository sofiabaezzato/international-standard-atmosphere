// Centralized API service using axios
import axios from 'axios'
import { apiConfig } from '../config/api.js'

// Create axios instance with environment-based configuration
const api = axios.create(apiConfig)

// Add request interceptor for logging in development
api.interceptors.request.use(
  (config) => {
    if (import.meta.env.DEV) {
      console.log(`API Request: ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`)
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (import.meta.env.DEV) {
      console.error('API Error:', error.response?.data || error.message)
    }
    
    // Handle specific error cases
    if (error.response?.status === 429) {
      const retryAfter = error.response.headers['retry-after']
      throw new Error(
        `Rate limit exceeded. ${error.response.data?.message || 'Please wait before making another request.'}${
          retryAfter ? ` Retry after ${retryAfter} seconds.` : ''
        }`
      )
    }
    
    throw error
  }
)

export default api