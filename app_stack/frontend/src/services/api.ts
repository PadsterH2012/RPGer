/**
 * API service configuration
 * Configures axios with base URL and interceptors
 */

import axios from 'axios';

// Get the API URL from environment variables or use default
let API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5002';

// If we're running in a browser and the URL contains 'rpger-backend', replace it with 'localhost'
if (typeof window !== 'undefined' && API_URL.includes('rpger-backend')) {
  API_URL = API_URL.replace('rpger-backend', 'localhost');
}

console.log('API Service initialized with URL:', API_URL);

// Create axios instance with custom config
const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // You can add auth tokens or other headers here
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle common errors here
    if (error.response) {
      // Server responded with an error status
      console.error('API Error:', error.response.status, error.response.data);
    } else if (error.request) {
      // Request was made but no response received
      console.error('API Error: No response received', error.request);
    } else {
      // Something else happened while setting up the request
      console.error('API Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export default api;
