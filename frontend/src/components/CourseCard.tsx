/**
 * Компонент карточки курса
 */

import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { favoritesApi, type Course } from '../api/client'

interface CourseCardProps {
  course: Course
}

const CourseCard = ({ course }: CourseCardProps) => {
  const [isFavorite, setIsFavorite] = useState(false)
  const [loadingFavorite, setLoadingFavorite] = useState(false)

  useEffect(() => {
    checkFavorite()
  }, [course.id])

  const checkFavorite = async () => {
    try {
      const response = await favoritesApi.check(course.id)
      console.log('🔍 [CourseCard] Проверка избранного для курса:', course.id, 'результат:', response.data.is_favorite)
      setIsFavorite(response.data.is_favorite)
    } catch (error: any) {
      console.warn('⚠️ [CourseCard] Ошибка проверки избранного:', error)
      // Если ошибка - считаем что курс не в избранном
      setIsFavorite(false)
    }
  }

  const handleFavoriteClick = async (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    if (loadingFavorite) return
    
    try {
      setLoadingFavorite(true)
      console.log('❤️ [CourseCard] Изменение избранного для курса:', course.id, 'текущее состояние:', isFavorite)
      
      if (isFavorite) {
        try {
          const response = await favoritesApi.remove(course.id)
          console.log('✅ [CourseCard] Курс удален из избранного:', response.data)
          setIsFavorite(false)
          // Отправляем событие для обновления списка избранного в профиле
          window.dispatchEvent(new CustomEvent('favorite_changed'))
          // Показываем уведомление (опционально)
          if (window.Telegram?.WebApp) {
            window.Telegram.WebApp.showAlert('Курс удален из избранного')
          }
        } catch (removeError: any) {
          console.error('❌ [CourseCard] Ошибка удаления из избранного:', removeError)
          // Если курс уже не в избранном - просто обновляем состояние
          if (removeError.response?.status === 404 || removeError.response?.data?.message?.includes('не в избранном')) {
            setIsFavorite(false)
            return
          }
          throw removeError
        }
      } else {
        try {
          const response = await favoritesApi.add(course.id)
          console.log('✅ [CourseCard] Курс добавлен в избранное:', response.data)
          setIsFavorite(true)
          // Отправляем событие для обновления списка избранного в профиле
          window.dispatchEvent(new CustomEvent('favorite_changed'))
          // Показываем уведомление (опционально)
          if (window.Telegram?.WebApp) {
            window.Telegram.WebApp.showAlert('Курс добавлен в избранное')
          }
        } catch (addError: any) {
          console.error('❌ [CourseCard] Ошибка добавления в избранное:', addError)
          // Если курс уже в избранном - просто обновляем состояние
          if (addError.response?.data?.message?.includes('уже в избранном') || 
              addError.response?.data?.is_favorite === true) {
            setIsFavorite(true)
            if (window.Telegram?.WebApp) {
              window.Telegram.WebApp.showAlert('Курс уже в избранном')
            }
            return
          }
          throw addError
        }
      }
    } catch (error: any) {
      console.error('❌ [CourseCard] Критическая ошибка изменения избранного:', error)
      console.error('   Статус:', error.response?.status)
      console.error('   Данные:', error.response?.data)
      
      // Показываем более понятное сообщение об ошибке
      let errorMessage = 'Ошибка при изменении избранного'
      
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message
      } else if (error.message) {
        errorMessage = error.message
      }
      
      // Не показываем ошибку, если это просто дубликат
      if (!errorMessage.includes('уже') && !errorMessage.includes('не в избранном')) {
        if (window.Telegram?.WebApp) {
          window.Telegram.WebApp.showAlert(`Ошибка: ${errorMessage}`)
        } else {
          alert(`Ошибка: ${errorMessage}`)
        }
      }
    } finally {
      setLoadingFavorite(false)
    }
  }
  // Безопасно нормализуем все значения - гарантируем что это примитивы
  const courseId = typeof course?.id === 'number' && !isNaN(course.id) ? course.id : 0
  const courseTitle = typeof course?.title === 'string' ? course.title : 'Без названия'
  const courseDescription = typeof course?.description === 'string' ? course.description : ''
  const coverImageUrl = typeof course?.cover_image_url === 'string' && course.cover_image_url.trim() !== '' ? course.cover_image_url : null
  const isTop = course?.is_top === true
  const category = typeof course?.category === 'string' ? course.category : ''
  const durationHours = typeof course?.duration_hours === 'number' && !isNaN(course.duration_hours) && course.duration_hours > 0 ? course.duration_hours : null
  const price = typeof course?.price === 'number' && !isNaN(course.price) && course.price > 0 ? course.price : null
  
  return (
    <Link to={`/courses/${courseId}`} className="course-card" style={{ position: 'relative' }}>
      {/* Кнопка избранного */}
      <button
        onClick={handleFavoriteClick}
        style={{
          position: 'absolute',
          top: '10px',
          right: '10px',
          zIndex: 10,
          background: 'rgba(255, 255, 255, 0.9)',
          border: 'none',
          borderRadius: '50%',
          width: '40px',
          height: '40px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer',
          fontSize: '20px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}
        title={isFavorite ? 'Удалить из избранного' : 'Добавить в избранное'}
        disabled={loadingFavorite}
      >
        {loadingFavorite ? '⏳' : (isFavorite ? '❤️' : '🤍')}
      </button>

      {/* Обложка курса */}
      {coverImageUrl && (
        <div className="course-cover">
          <img src={coverImageUrl} alt={courseTitle} />
        </div>
      )}

      {/* Информация о курсе */}
      <div className="course-info">
        {isTop && <span className="badge-top">🔥 Топ</span>}
        
        <h3 className="course-title">{courseTitle}</h3>
        <p className="course-description">{courseDescription}</p>
        
        <div className="course-meta">
          <span className="category">{getCategoryLabel(category)}</span>
          {durationHours !== null && (
            <span className="duration">⏱ {durationHours} ч</span>
          )}
        </div>

        {price !== null && (
          <div className="course-price">{price} ₽</div>
        )}
      </div>
    </Link>
  )
}

// Маппинг категорий на русские названия
function getCategoryLabel(category: string): string {
  const labels: Record<string, string> = {
    manicure: 'Маникюр',
    pedicure: 'Педикюр',
    eyelashes: 'Ресницы',
    eyebrows: 'Брови',
    podology: 'Подология',
    marketing: 'Маркетинг',
    business: 'Своё дело',
  }
  return labels[category] || category
}

export default CourseCard

