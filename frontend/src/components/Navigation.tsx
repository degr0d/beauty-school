/**
 * Компонент навигации (фиксированная панель)
 */

import { Link, useLocation } from 'react-router-dom'

const Navigation = () => {
  const location = useLocation()

  const navItems = [
    { path: '/', label: '🏠 Главная', icon: '🏠' },
    { path: '/courses', label: '📚 Курсы', icon: '📚' },
    { path: '/challenges', label: '🎯 Челленджи', icon: '🎯' },
    { path: '/communities', label: '💬 Сообщества', icon: '💬' },
    { path: '/profile', label: '👤 Профиль', icon: '👤' },
  ]

  return (
    <nav className="navigation">
      {navItems.map((item) => (
        <Link
          key={item.path}
          to={item.path}
          className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
        >
          <span className="nav-icon">{item.icon}</span>
          <span className="nav-label">{item.label.replace(/^\S+ /, '')}</span>
        </Link>
      ))}
    </nav>
  )
}

export default Navigation

