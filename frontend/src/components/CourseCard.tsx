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
      const isFavoriteValue = response.data?.is_favorite === true
      console.log('🔍 [CourseCard] Проверка избранного для курса:', course.id, 'результат:', isFavoriteValue)
      setIsFavorite(isFavoriteValue)
    } catch (error: any) {
      console.warn('⚠️ [CourseCard] Ошибка проверки избранного:', error)
      console.warn('   Статус:', error.response?.status)
      console.warn('   Данные:', error.response?.data)
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
      console.log('📤 [CourseCard] Отправка запроса...')
      
      if (isFavorite) {
        try {
          const response = await favoritesApi.remove(course.id)
          console.log('✅ [CourseCard] Курс удален из избранного:', response.data)
          setIsFavorite(false)
          window.dispatchEvent(new CustomEvent('favorite_changed'))
        } catch (removeError: any) {
          console.error('❌ [CourseCard] Ошибка удаления из избранного:', removeError)
          console.error('   Тип ошибки:', removeError.constructor.name)
          console.error('   Сообщение:', removeError.message)
          console.error('   Статус:', removeError.response?.status)
          console.error('   Данные ответа:', removeError.response?.data)
          console.error('   Запрос:', removeError.config?.url, removeError.config?.method)
          
          // Если курс уже не в избранном - просто обновляем состояние
          if (removeError.response?.status === 404 || 
              removeError.response?.data?.message?.includes('не в избранном') ||
              removeError.response?.data?.detail?.includes('не в избранном')) {
            console.log('ℹ️ [CourseCard] Курс уже не в избранном, обновляем состояние')
            setIsFavorite(false)
            return
          }
          
          // Если это Network Error - пробуем еще раз через небольшую задержку
          if (!removeError.response && removeError.message?.includes('Network')) {
            console.warn('⚠️ [CourseCard] Network Error, пробуем еще раз...')
            await new Promise(resolve => setTimeout(resolve, 500))
            try {
              const retryResponse = await favoritesApi.remove(course.id)
              console.log('✅ [CourseCard] Повторная попытка успешна:', retryResponse.data)
              setIsFavorite(false)
              window.dispatchEvent(new CustomEvent('favorite_changed'))
              return
            } catch (retryError: any) {
              console.error('❌ [CourseCard] Повторная попытка тоже не удалась:', retryError)
            }
          }
          
          throw removeError
        }
      } else {
        try {
          const response = await favoritesApi.add(course.id)
          console.log('✅ [CourseCard] Курс добавлен в избранное:', response.data)
          setIsFavorite(true)
          window.dispatchEvent(new CustomEvent('favorite_changed'))
        } catch (addError: any) {
          console.error('❌ [CourseCard] Ошибка добавления в избранное:', addError)
          console.error('   Тип ошибки:', addError.constructor.name)
          console.error('   Сообщение:', addError.message)
          console.error('   Статус:', addError.response?.status)
          console.error('   Данные ответа:', addError.response?.data)
          console.error('   Запрос:', addError.config?.url, addError.config?.method)
          
          // Если курс уже в избранном - просто обновляем состояние
          if (addError.response?.data?.message?.includes('уже в избранном') || 
              addError.response?.data?.is_favorite === true ||
              addError.response?.data?.detail?.includes('уже в избранном')) {
            console.log('ℹ️ [CourseCard] Курс уже в избранном, обновляем состояние')
            setIsFavorite(true)
            return
          }
          
          // Если это Network Error - пробуем еще раз через небольшую задержку
          if (!addError.response && addError.message?.includes('Network')) {
            console.warn('⚠️ [CourseCard] Network Error, пробуем еще раз...')
            await new Promise(resolve => setTimeout(resolve, 500))
            try {
              const retryResponse = await favoritesApi.add(course.id)
              console.log('✅ [CourseCard] Повторная попытка успешна:', retryResponse.data)
              setIsFavorite(true)
              window.dispatchEvent(new CustomEvent('favorite_changed'))
              return
            } catch (retryError: any) {
              console.error('❌ [CourseCard] Повторная попытка тоже не удалась:', retryError)
            }
          }
          
          throw addError
        }
      }
    } catch (error: any) {
      console.error('❌ [CourseCard] Критическая ошибка изменения избранного:', error)
      console.error('   Полная информация об ошибке:', {
        name: error.name,
        message: error.message,
        stack: error.stack,
        response: error.response ? {
          status: error.response.status,
          statusText: error.response.statusText,
          data: error.response.data,
          headers: error.response.headers
        } : null,
        request: error.config ? {
          url: error.config.url,
          method: error.config.method,
          headers: error.config.headers
        } : null
      })
      
      // Показываем более понятное сообщение об ошибке
      let errorMessage = 'Ошибка при изменении избранного'
      
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message
      } else if (error.message) {
        errorMessage = error.message
      }
      
      // Не показываем ошибку, если это просто дубликат или Network Error (уже обработан)
      if (!errorMessage.includes('уже') && 
          !errorMessage.includes('не в избранном') &&
          !error.message?.includes('Network')) {
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

