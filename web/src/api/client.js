const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'
const TOKEN_KEY = 'todo_token'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
}

function buildQuery(params) {
  const entries = Object.entries(params || {})
    .filter(([, value]) => value !== undefined && value !== null && value !== '')
    .map(([key, value]) => [key, String(value)])
  if (!entries.length) return ''
  const search = new URLSearchParams(entries)
  return `?${search.toString()}`
}

export async function request(path, options = {}) {
  const token = getToken()
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  }
  if (token) headers.Authorization = `Bearer ${token}`
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  })
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    if (response.status === 401) clearToken()
    const error = new Error(payload?.message || 'request_failed')
    error.code = payload?.code || response.status
    throw error
  }
  if (payload?.code !== 0) {
    if (payload?.code === 40101) clearToken()
    const error = new Error(payload?.message || 'request_failed')
    error.code = payload?.code
    throw error
  }
  return payload.data
}

export function get(path, params) {
  return request(`${path}${buildQuery(params)}`)
}

export function post(path, body) {
  return request(path, { method: 'POST', body: JSON.stringify(body || {}) })
}

export function put(path, body) {
  return request(path, { method: 'PUT', body: JSON.stringify(body || {}) })
}

export function patch(path, body) {
  return request(path, { method: 'PATCH', body: JSON.stringify(body || {}) })
}

export function del(path) {
  return request(path, { method: 'DELETE' })
}
