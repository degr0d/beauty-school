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
    
    if (loadingFavorite) {
      console.log('⏳ [CourseCard] Уже идет загрузка, игнорируем клик')
      return
    }
    
    // Оптимистичное обновление UI - сразу меняем состояние
    const previousState = isFavorite
    const newState = !isFavorite
    setIsFavorite(newState)
    setLoadingFavorite(true)
    
    console.log('❤️ [CourseCard] Изменение избранного для курса:', course.id)
    console.log('   Текущее состояние:', previousState, '→ Новое состояние:', newState)
    console.log('   Оптимистичное обновление UI применено')
    
    try {
      if (previousState) {
        // Удаляем из избранного
        console.log('📤 [CourseCard] Отправка запроса на удаление...')
        try {
          const response = await favoritesApi.remove(course.id)
          console.log('✅ [CourseCard] Курс удален из избранного:', response.data)
          window.dispatchEvent(new CustomEvent('favorite_changed'))
        } catch (removeError: any) {
          console.error('❌ [CourseCard] Ошибка удаления из избранного:', removeError)
          console.error('   Тип ошибки:', removeError.constructor?.name || typeof removeError)
          console.error('   Сообщение:', removeError.message)
          console.error('   Статус:', removeError.response?.status)
          console.error('   Данные ответа:', removeError.response?.data)
          console.error('   URL запроса:', removeError.config?.url)
          
          // Откатываем оптимистичное обновление
          setIsFavorite(previousState)
          
          // Если курс уже не в избранном - это нормально
          if (removeError.response?.status === 404 || 
              removeError.response?.data?.message?.includes('не в избранном') ||
              removeError.response?.data?.detail?.includes('не в избранном')) {
            console.log('ℹ️ [CourseCard] Курс уже не в избранном - состояние корректно')
            return
          }
          
          // Если это Network Error - пробуем еще раз
          if (!removeError.response && (removeError.message?.includes('Network') || removeError.code === 'ERR_NETWORK')) {
            console.warn('⚠️ [CourseCard] Network Error, пробуем еще раз через 500мс...')
            await new Promise(resolve => setTimeout(resolve, 500))
            try {
              const retryResponse = await favoritesApi.remove(course.id)
              console.log('✅ [CourseCard] Повторная попытка успешна:', retryResponse.data)
              setIsFavorite(false)
              window.dispatchEvent(new CustomEvent('favorite_changed'))
              return
            } catch (retryError: any) {
              console.error('❌ [CourseCard] Повторная попытка тоже не удалась:', retryError)
              setIsFavorite(previousState)
            }
          }
          
          throw removeError
        }
      } else {
        // Добавляем в избранное
        console.log('📤 [CourseCard] Отправка запроса на добавление...')
        try {
          const response = await favoritesApi.add(course.id)
          console.log('✅ [CourseCard] Курс добавлен в избранное:', response.data)
          window.dispatchEvent(new CustomEvent('favorite_changed'))
        } catch (addError: any) {
          console.error('❌ [CourseCard] Ошибка добавления в избранное:', addError)
          console.error('   Тип ошибки:', addError.constructor?.name || typeof addError)
          console.error('   Сообщение:', addError.message)
          console.error('   Статус:', addError.response?.status)
          console.error('   Данные ответа:', addError.response?.data)
          console.error('   URL запроса:', addError.config?.url)
          
          // Откатываем оптимистичное обновление
          setIsFavorite(previousState)
          
          // Если курс уже в избранном - обновляем состояние
          if (addError.response?.data?.message?.includes('уже в избранном') || 
              addError.response?.data?.is_favorite === true ||
              addError.response?.data?.detail?.includes('уже в избранном')) {
            console.log('ℹ️ [CourseCard] Курс уже в избранном, обновляем состояние')
            setIsFavorite(true)
            return
          }
          
          // Если это Network Error - пробуем еще раз
          if (!addError.response && (addError.message?.includes('Network') || addError.code === 'ERR_NETWORK')) {
            console.warn('⚠️ [CourseCard] Network Error, пробуем еще раз через 500мс...')
            await new Promise(resolve => setTimeout(resolve, 500))
            try {
              const retryResponse = await favoritesApi.add(course.id)
              console.log('✅ [CourseCard] Повторная попытка успешна:', retryResponse.data)
              setIsFavorite(true)
              window.dispatchEvent(new CustomEvent('favorite_changed'))
              return
            } catch (retryError: any) {
              console.error('❌ [CourseCard] Повторная попытка тоже не удалась:', retryError)
              setIsFavorite(previousState)
            }
          }
          
          throw addError
        }
      }
    } catch (error: any) {
      console.error('❌ [CourseCard] Критическая ошибка изменения избранного:', error)
      
      // Показываем ошибку только если это не дубликат и не Network Error
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message || 
                          error.message || 
                          'Ошибка при изменении избранного'
      
      if (!errorMessage.includes('уже') && 
          !errorMessage.includes('не в избранном') &&
          !error.message?.includes('Network') &&
          error.code !== 'ERR_NETWORK') {
        if (window.Telegram?.WebApp) {
          window.Telegram.WebApp.showAlert(`Ошибка: ${errorMessage}`)
        } else {
          alert(`Ошибка: ${errorMessage}`)
        }
      }
    } finally {
      setLoadingFavorite(false)
      console.log('🏁 [CourseCard] Завершена обработка клика, loadingFavorite:', false)
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

