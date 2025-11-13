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
      setIsFavorite(response.data.is_favorite)
    } catch (error) {
      // Игнорируем ошибки при проверке избранного
    }
  }

  const handleFavoriteClick = async (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    if (loadingFavorite) return
    
    try {
      setLoadingFavorite(true)
      if (isFavorite) {
        await favoritesApi.remove(course.id)
        setIsFavorite(false)
      } else {
        await favoritesApi.add(course.id)
        setIsFavorite(true)
      }
    } catch (error) {
      console.error('Ошибка изменения избранного:', error)
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
      >
        {isFavorite ? '❤️' : '🤍'}
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

