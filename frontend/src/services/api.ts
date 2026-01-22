import axios from 'axios'
import { DEFAULT_API_URL, CONTENT_TYPE_JSON } from '@/constants/global'

const getApiUrl = () => {
  const envUrl = import.meta.env.VITE_API_URL

  if (envUrl) {
    return envUrl
  }

  if (typeof window !== 'undefined') {
    const protocol = window.location.protocol.replace(':', '')
    const hostname = window.location.hostname
    const port = window.location.port

    if (port) {
      return `${protocol}://${hostname}:${port}`
    }
    return `${protocol}://${hostname}`
  }

  return DEFAULT_API_URL
}

const apiClient = axios.create({
  baseURL: getApiUrl(),
  headers: {
    'Content-Type': CONTENT_TYPE_JSON,
  },
})

export default apiClient
