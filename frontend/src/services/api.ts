import axios from 'axios'
import { DEFAULT_API_PORT, DEFAULT_API_PROTOCOL, DEFAULT_API_URL, CONTENT_TYPE_JSON } from '@/constants/global'

const getApiUrl = () => {
  const envUrl = import.meta.env.VITE_API_URL
  if (typeof window !== 'undefined' && window.location.hostname !== 'localhost') {
    return `${DEFAULT_API_PROTOCOL}://${window.location.hostname}:${DEFAULT_API_PORT}`
  }
  return envUrl || DEFAULT_API_URL
}

const apiClient = axios.create({
  baseURL: getApiUrl(),
  headers: {
    'Content-Type': CONTENT_TYPE_JSON
  }
})

export default apiClient
