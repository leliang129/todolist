import { getToken, setToken, post } from './client'

const DEMO_USER = {
  username: 'demo',
  password: '123456',
  email: 'demo@example.com',
}

export async function ensureAuth() {
  const token = getToken()
  if (token) return token
  try {
    const login = await post('/auth/login', {
      username: DEMO_USER.username,
      password: DEMO_USER.password,
    })
    setToken(login.access_token)
    return login.access_token
  } catch (err) {
    try {
      await post('/auth/register', DEMO_USER)
    } catch (_) {
      // ignore register errors (e.g. already exists)
    }
    const login = await post('/auth/login', {
      username: DEMO_USER.username,
      password: DEMO_USER.password,
    })
    setToken(login.access_token)
    return login.access_token
  }
}
