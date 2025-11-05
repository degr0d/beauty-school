/**
 * Страница детального просмотра курса
 */

import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { coursesApi, progressApi, paymentApi, type CourseDetail, type CourseProgress } from '../api/client'
import LessonItem from '../components/LessonItem'
import ProgressBar from '../components/ProgressBar'

const CoursePage = () => {
  const { id } = useParams<{ id: string }>()
  const [course, setCourse] = useState<CourseDetail | null>(null)
  const [progress, setProgress] = useState<CourseProgress | null>(null)
  const [loading, setLoading] = useState(true)
  const [isPurchased, setIsPurchased] = useState(false)
  const [purchasing, setPurchasing] = useState(false)

  useEffect(() => {
    if (id) {
      loadCourse(parseInt(id))
      loadProgress(parseInt(id))
      checkPurchaseStatus(parseInt(id))
    }
  }, [id])
  
  const checkPurchaseStatus = async (courseId: number) => {
    try {
      const response = await coursesApi.getMy()
      const myCourses = response.data
      const purchased = myCourses.some((c: any) => c.id === courseId)
      setIsPurchased(purchased)
    } catch (error) {
      console.error('Ошибка проверки покупки:', error)
      setIsPurchased(false)
    }
  }
  
  const handlePurchase = async () => {
    if (!course || isPurchased) return
    
    setPurchasing(true)
    try {
      const response = await paymentApi.create(course.id)
      window.location.href = response.data.payment_url
    } catch (error: any) {
      console.error('Ошибка создания платежа:', error)
      alert(error.response?.data?.detail || 'Ошибка при создании платежа')
      setPurchasing(false)
    }
  }

  const loadCourse = async (courseId: number) => {
    try {
      const response = await coursesApi.getById(courseId)
      setCourse(response.data)
    } catch (error) {
      console.error('Ошибка загрузки курса:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadProgress = async (courseId: number) => {
    try {
      const response = await progressApi.getByCourse(courseId)
      setProgress(response.data)
    } catch (error) {
      console.error('Ошибка загрузки прогресса:', error)
    }
  }

  if (loading) {
    return <div className="loading">Загрузка...</div>
  }

  if (!course) {
    return <div className="error">Курс не найден</div>
  }

  return (
    <div className="course-page">
      {/* Обложка */}
      {course.cover_image_url && (
        <div className="course-header-image">
          <img src={course.cover_image_url} alt={course.title} />
        </div>
      )}

      {/* Информация о курсе */}
      <div className="course-header">
        <h1>{course.title}</h1>
        <p className="course-category">{course.category}</p>
        <p className="course-description">{course.description}</p>

        {course.full_description && (
          <div className="course-full-description">
            <p>{course.full_description}</p>
          </div>
        )}

        {/* Цена и кнопка покупки */}
        {course.price > 0 && (
          <div className="course-purchase">
            <div className="course-price">
              <span className="price-value">{course.price} ₽</span>
            </div>
            {!isPurchased ? (
              <button 
                className="purchase-btn"
                onClick={handlePurchase}
                disabled={purchasing}
              >
                {purchasing ? 'Обработка...' : 'Купить курс'}
              </button>
            ) : (
              <div className="purchased-badge">
                ✅ Курс куплен
              </div>
            )}
          </div>
        )}

        {/* Прогресс */}
        {progress && isPurchased && (
          <div className="course-progress">
            <h3>Твой прогресс</h3>
            <ProgressBar percent={progress.progress_percent} />
            <p className="progress-text">
              Пройдено уроков: {progress.completed_lessons} / {progress.total_lessons}
            </p>
          </div>
        )}
      </div>

      {/* Список уроков */}
      <div className="course-lessons">
        <h2>📖 Уроки</h2>
        {!isPurchased && course.price > 0 ? (
          <div className="course-locked">
            <p>🔒 Для доступа к урокам необходимо купить курс</p>
            <p className="preview-note">
              {course.lessons.filter(l => l.is_free).length > 0 && (
                <span>Доступно {course.lessons.filter(l => l.is_free).length} бесплатных уроков для просмотра</span>
              )}
            </p>
          </div>
        ) : (
          <>
            {course.lessons.length > 0 ? (
              <div className="lessons-list">
                {course.lessons.map((lesson) => {
                  const lessonProgress = progress?.lessons.find(l => l.id === lesson.id)
                  return (
                    <LessonItem
                      key={lesson.id}
                      lesson={{ ...lesson, completed: lessonProgress?.completed }}
                      courseId={course.id}
                    />
                  )
                })}
              </div>
            ) : (
              <p>Уроков пока нет</p>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default CoursePage

