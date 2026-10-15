import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '@/context/auth-context'
import { Button } from '@/components/ui/button'

function AuthNav() {
  const { user, loading, logout } = useAuth()
  const navigate = useNavigate()

  // a saved token is still being checked: show nothing, so there is no flash of "Log in"
  if (loading) {
    return null
  }

  if (!user) {
    return (
      <>
        <Link to="/login" className="font-body text-ink hover:text-primary">
          Log in
        </Link>
        <Link
          to="/register"
          className="bg-highlight hover:bg-highlight-dark text-white font-medium px-4 py-2 rounded-full"
        >
          Sign up
        </Link>
      </>
    )
  }

  function handleLogout() {
    logout()
    navigate('/')
  }

  return (
    <>
      <span className="font-body text-sm text-ink/70 max-w-48 truncate">{user.email}</span>
      <Button type="button" variant="outline" size="sm" onClick={handleLogout}>
        Log out
      </Button>
    </>
  )
}

export default AuthNav
