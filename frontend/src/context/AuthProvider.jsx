import { useEffect, useState } from 'react'
import { fetchMe, loginUser, logoutUser, registerUser } from '../api/auth'
import { AuthContext } from './auth-context'

// older versions kept the login token in localStorage; remove it if it is still there
function removeOldToken() {
  try {
    localStorage.removeItem('kitepche_token')
  } catch {
    // storage unavailable: nothing to remove
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // on page load: the browser sends the login cookie (if there is one); ask who it belongs to
  useEffect(() => {
    removeOldToken()

    let cancelled = false
    fetchMe()
      .then((me) => {
        if (!cancelled) setUser(me)
      })
      .catch(() => {
        // 401 means not logged in; a network error also leaves the page logged out
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [])

  async function login(email, password) {
    const me = await loginUser(email, password)
    setUser(me)
    return me
  }

  async function register(email, password) {
    await registerUser(email, password)
    return login(email, password)
  }

  async function logout() {
    try {
      await logoutUser()
    } catch {
      // the server could not be reached: the cookie stays until it expires
    }
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

