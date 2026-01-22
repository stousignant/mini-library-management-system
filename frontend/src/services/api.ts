import axios from 'axios'

const getApiUrl = () => {
  const envUrl = import.meta.env.VITE_API_URL
  if (typeof window !== 'undefined' && window.location.hostname !== 'localhost') {
    return `http://${window.location.hostname}:8000`
  }
  return envUrl || 'http://localhost:8000'
}

const apiClient = axios.create({
  baseURL: getApiUrl(),
  headers: {
    'Content-Type': 'application/json'
  }
})

export default apiClient
