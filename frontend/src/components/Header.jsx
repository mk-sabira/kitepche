import { Link, NavLink } from 'react-router-dom'

const navClass = ({ isActive }) =>
  `font-body ${isActive ? 'text-primary font-semibold' : 'text-ink hover:text-primary'}`

function Header() {
  return (
    <header className="flex items-center justify-between px-8 py-4 bg-paper border-b border-paper-soft">
      <Link to="/" className="flex items-center gap-2">
        <span className="text-2xl">📖</span>
        <span className="font-display text-2xl font-semibold text-primary">Kitepche</span>
      </Link>

      <nav className="flex items-center gap-6 font-body">
        <NavLink to="/" end className={navClass}>
          Home
        </NavLink>
        <a href="/#library" className="text-ink hover:text-primary">
          Library
        </a>
        <NavLink to="/analyze" className={navClass}>
          Analyze
        </NavLink>
        <button className="bg-highlight hover:bg-highlight-dark text-white font-medium px-4 py-2 rounded-full">
          Login
        </button>
      </nav>
    </header>
  )
}

export default Header
