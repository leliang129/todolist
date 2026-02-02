import { clearToken, get, getToken, post, setToken } from './client'

export async function validateToken() {
  const token = getToken()
  if (!token) return null
  try {
    const user = await get('/users/me')
    return user
  } catch (_) {
    clearToken()
    return null
  }
}

export async function login(username, password) {
  const data = await post('/auth/login', { username, password })
  setToken(data.access_token)
  return data
}

export function logout() {
  clearToken()
}
