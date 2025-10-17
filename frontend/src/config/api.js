// API Configuration
// Vite automatically loads the correct .env file based on the mode (development/production)

const config = {
  // API Base URL from environment variables
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  
  // App Environment
  appEnv: import.meta.env.VITE_APP_ENV || 'development',
  
  // Development flag
  isDevelopment: import.meta.env.DEV,
  
  // Production flag  
  isProduction: import.meta.env.PROD,
}

// Axios default configuration
export const apiConfig = {
  baseURL: config.apiBaseUrl,
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  }
}

// Export individual values for convenience
export const { apiBaseUrl, appEnv, isDevelopment, isProduction } = config

// Default export
export default config