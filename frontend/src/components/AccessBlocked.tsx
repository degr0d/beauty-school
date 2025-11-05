/**
 * Компонент блокировки доступа
 * Показывается если пользователь не оплатил ни одного курса
 */

import { Link } from 'react-router-dom'

interface AccessBlockedProps {
  onViewCourses?: () => void
}

const AccessBlocked = ({ onViewCourses }: AccessBlockedProps) => {
  return (
    <div className="access-blocked">
      <div className="access-blocked-content">
        <div className="lock-icon">🔒</div>
        <h1>Доступ ограничен</h1>
        <p className="access-message">
          Для доступа к платформе необходимо приобрести хотя бы один курс.
        </p>
        <p className="access-subtitle">
          Выберите курс и оплатите его, чтобы получить полный доступ ко всем материалам.
        </p>
        
        <div className="access-actions">
          {onViewCourses ? (
            <button onClick={onViewCourses} className="btn-primary">
              📚 Выбрать курс
            </button>
          ) : (
            <Link to="/courses" className="btn-primary">
              📚 Выбрать курс
            </Link>
          )}
        </div>
        
        <div className="access-benefits">
          <h3>Что вы получите:</h3>
          <ul>
            <li>✅ Доступ ко всем материалам курсов</li>
            <li>✅ Видео-уроки и PDF материалы</li>
            <li>✅ Отслеживание прогресса обучения</li>
            <li>✅ Доступ к сообществам</li>
            <li>✅ Сертификаты по завершении</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default AccessBlocked

