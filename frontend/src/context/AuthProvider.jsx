import { useEffect, useState } from 'react'
import { fetchMe, loginUser, registerUser } from '../api/auth'
import { AuthContext } from './auth-context'

const TOKEN_KEY = 'kitepche_token'

function readToken() {
  try {
    return localStorage.getItem(TOKEN_KEY)
  } catch {
    return null
  }
}

function saveToken(token) {
  try {
    localStorage.setItem(TOKEN_KEY, token)
  } catch {
    // storage unavailable: the user stays logged in until the page is closed
  }
}

function clearToken() {
  try {
    localStorage.removeItem(TOKEN_KEY)
  } catch {
    // nothing to clear
  }
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(readToken)
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(() => readToken() !== null)

  // on page load: if a token was saved, find out who it belongs to
  useEffect(() => {
    const saved = readToken()
    if (!saved) return

    let cancelled = false
    fetchMe(saved)
      .then((me) => {
        if (!cancelled) setUser(me)
      })
      .catch((err) => {
        if (cancelled) return
        if (err.status === 401) {
          clearToken()
          setToken(null)
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [])

  async function login(email, password) {
    const { access_token } = await loginUser(email, password)
    const me = await fetchMe(access_token)
    saveToken(access_token)
    setToken(access_token)
    setUser(me)
    return me
  }

  async function register(email, password) {
    await registerUser(email, password)
    return login(email, password)
  }

  function logout() {
    clearToken()
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ token, user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}