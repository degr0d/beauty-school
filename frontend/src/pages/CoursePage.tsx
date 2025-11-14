/**
 * Страница детального просмотра курса
 */

import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { coursesApi, progressApi, paymentApi, favoritesApi, type CourseDetail, type CourseProgress } from '../api/client'
import LessonItem from '../components/LessonItem'
import ProgressBar from '../components/ProgressBar'
import ReviewsSection from '../components/ReviewsSection'

const CoursePage = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [course, setCourse] = useState<CourseDetail | null>(null)
  const [progress, setProgress] = useState<CourseProgress | null>(null)
  const [loading, setLoading] = useState(true)
  const [isPurchased, setIsPurchased] = useState(false)
  const [purchasing, setPurchasing] = useState(false)
  const [isFavorite, setIsFavorite] = useState(false)
  const [loadingFavorite, setLoadingFavorite] = useState(false)

  useEffect(() => {
    if (id) {
      loadCourse(parseInt(id))
      loadProgress(parseInt(id))
      checkPurchaseStatus(parseInt(id))
      checkFavoriteStatus(parseInt(id))
    }
  }, [id])

  const checkFavoriteStatus = async (courseId: number) => {
    try {
      const response = await favoritesApi.check(courseId)
      setIsFavorite(response.data.is_favorite)
    } catch (error) {
      console.error('Ошибка проверки избранного:', error)
    }
  }

  const handleFavoriteClick = async () => {
    if (!id || loadingFavorite) return
    
    try {
      setLoadingFavorite(true)
      if (isFavorite) {
        try {
          await favoritesApi.remove(parseInt(id))
          setIsFavorite(false)
          // Отправляем событие для обновления списка избранного в профиле
          window.dispatchEvent(new CustomEvent('favorite_changed'))
        } catch (removeError: any) {
          // Если курс уже не в избранном - просто обновляем состояние
          if (removeError.response?.status === 404 || removeError.response?.data?.message?.includes('не в избранном')) {
            setIsFavorite(false)
            return
          }
          throw removeError
        }
      } else {
        try {
          const response = await favoritesApi.add(parseInt(id))
          setIsFavorite(true)
          // Отправляем событие для обновления списка избранного в профиле
          window.dispatchEvent(new CustomEvent('favorite_changed'))
          // Если курс уже был в избранном - показываем сообщение
          if (response.data?.message?.includes('уже в избранном')) {
            if (window.Telegram?.WebApp) {
              window.Telegram.WebApp.showAlert('Курс уже в избранном')
            }
          }
        } catch (addError: any) {
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
      console.error('Ошибка изменения избранного:', error)
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Ошибка при изменении избранного'
      // Не показываем ошибку, если это просто дубликат
      if (!errorMessage.includes('уже') && !errorMessage.includes('не в избранном')) {
        if (window.Telegram?.WebApp) {
          window.Telegram.WebApp.showAlert(`Ошибка: ${errorMessage}`)
        }
      }
    } finally {
      setLoadingFavorite(false)
    }
  }

  // Обновляем прогресс при возврате на страницу (например, после завершения урока)
  useEffect(() => {
    const handleFocus = () => {
      if (id) {
        loadProgress(parseInt(id))
      }
    }
    window.addEventListener('focus', handleFocus)
    return () => window.removeEventListener('focus', handleFocus)
  }, [id])
  
  const checkPurchaseStatus = async (courseId: number) => {
    try {
      const response = await coursesApi.getMy()
      // Гарантируем что это массив
      const myCourses = Array.isArray(response.data) ? response.data : []
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
      const rawCourse = response.data
      
      // Нормализуем курс - гарантируем что все поля это примитивы
      if (rawCourse) {
        const normalizedCourse: CourseDetail = {
          id: typeof rawCourse.id === 'number' && !isNaN(rawCourse.id) ? rawCourse.id : 0,
          title: typeof rawCourse.title === 'string' ? rawCourse.title : 'Без названия',
          description: typeof rawCourse.description === 'string' ? rawCourse.description : '',
          category: typeof rawCourse.category === 'string' ? rawCourse.category : '',
          cover_image_url: typeof rawCourse.cover_image_url === 'string' && rawCourse.cover_image_url.trim() !== '' ? rawCourse.cover_image_url : undefined,
          is_top: rawCourse.is_top === true,
          price: typeof rawCourse.price === 'number' && !isNaN(rawCourse.price) ? rawCourse.price : 0,
          duration_hours: typeof rawCourse.duration_hours === 'number' && !isNaN(rawCourse.duration_hours) && rawCourse.duration_hours > 0 ? rawCourse.duration_hours : undefined,
          full_description: typeof rawCourse.full_description === 'string' ? rawCourse.full_description : undefined,
          lessons: Array.isArray(rawCourse.lessons) ? rawCourse.lessons.map((lesson: any) => ({
            id: typeof lesson?.id === 'number' && !isNaN(lesson.id) ? lesson.id : 0,
            title: typeof lesson?.title === 'string' ? lesson.title : 'Без названия',
            order: typeof lesson?.order === 'number' && !isNaN(lesson.order) ? lesson.order : 0,
            video_duration: typeof lesson?.video_duration === 'number' && !isNaN(lesson.video_duration) && lesson.video_duration > 0 ? lesson.video_duration : undefined,
            is_free: lesson?.is_free === true
          })) : []
        }
        setCourse(normalizedCourse)
      }
    } catch (error) {
      console.error('Ошибка загрузки курса:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadProgress = async (courseId: number) => {
    try {
      const response = await progressApi.getByCourse(courseId)
      const rawProgress = response.data
      
      // Нормализуем прогресс - гарантируем что все поля это примитивы
      if (rawProgress) {
        const normalizedProgress: CourseProgress = {
          course_id: typeof rawProgress.course_id === 'number' && !isNaN(rawProgress.course_id) ? rawProgress.course_id : 0,
          course_title: typeof rawProgress.course_title === 'string' ? rawProgress.course_title : '',
          total_lessons: typeof rawProgress.total_lessons === 'number' && !isNaN(rawProgress.total_lessons) ? rawProgress.total_lessons : 0,
          completed_lessons: typeof rawProgress.completed_lessons === 'number' && !isNaN(rawProgress.completed_lessons) ? rawProgress.completed_lessons : 0,
          progress_percent: typeof rawProgress.progress_percent === 'number' && !isNaN(rawProgress.progress_percent) ? Math.min(Math.max(rawProgress.progress_percent, 0), 100) : 0,
          lessons: Array.isArray(rawProgress.lessons) ? rawProgress.lessons.map((lesson: any) => ({
            id: typeof lesson?.id === 'number' && !isNaN(lesson.id) ? lesson.id : 0,
            title: typeof lesson?.title === 'string' ? lesson.title : '',
            order: typeof lesson?.order === 'number' && !isNaN(lesson.order) ? lesson.order : 0,
            completed: lesson?.completed === true
          })) : []
        }
        setProgress(normalizedProgress)
      }
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
      {/* Кнопка назад */}
      <div style={{ position: 'fixed', top: '10px', left: '10px', zIndex: 1000 }}>
        <button 
          onClick={() => navigate(-1)}
          style={{
            background: 'rgba(0, 0, 0, 0.5)',
            border: 'none',
            borderRadius: '50%',
            width: '40px',
            height: '40px',
            color: 'white',
            fontSize: '20px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backdropFilter: 'blur(10px)'
          }}
          title="Назад"
        >
          ←
        </button>
      </div>

      {/* Обложка */}
      {course.cover_image_url && (
        <div className="course-header-image">
          <img src={course.cover_image_url} alt={course.title} />
        </div>
      )}

      {/* Информация о курсе */}
      <div className="course-header">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '15px' }}>
          <h1 style={{ flex: 1, margin: 0 }}>{course.title}</h1>
          <button
            onClick={handleFavoriteClick}
            disabled={loadingFavorite}
            style={{
              background: 'transparent',
              border: '2px solid #e91e63',
              borderRadius: '50%',
              width: '50px',
              height: '50px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: loadingFavorite ? 'not-allowed' : 'pointer',
              fontSize: '24px',
              opacity: loadingFavorite ? 0.6 : 1,
              transition: 'all 0.3s ease'
            }}
            title={isFavorite ? 'Удалить из избранного' : 'Добавить в избранное'}
          >
            {isFavorite ? '❤️' : '🤍'}
          </button>
        </div>
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

        {/* Прогресс - показываем если есть прогресс (для админов или купленных курсов) */}
        {progress !== null && progress.total_lessons > 0 && (
          <div className="course-progress">
            <h3>Твой прогресс</h3>
            <ProgressBar percent={progress.progress_percent} />
            <p className="progress-text">
              Пройдено уроков: {progress.completed_lessons} / {progress.total_lessons}
              {progress.progress_percent === 100 && (
                <span style={{ color: '#4caf50', marginLeft: '10px' }}>✅ Курс завершен!</span>
              )}
            </p>
          </div>
        )}

        {/* Кнопка "Приступить к курсу" / "Продолжить" / "Попробовать бесплатно" */}
        {course.lessons.length > 0 && (() => {
          // Если курс не куплен, но есть первый урок - показываем кнопку "Попробовать бесплатно"
          if (!isPurchased && course.price > 0) {
            const firstLesson = course.lessons[0]
            if (firstLesson) {
              return (
                <div style={{ marginTop: '20px' }}>
                  <button
                    onClick={() => navigate(`/lessons/${firstLesson.id}`)}
                    style={{
                      width: '100%',
                      padding: '15px 20px',
                      backgroundColor: '#4CAF50',
                      color: 'white',
                      border: 'none',
                      borderRadius: '12px',
                      fontSize: '16px',
                      fontWeight: 'bold',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease',
                      boxShadow: '0 2px 8px rgba(76, 175, 80, 0.3)'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = '#45a049'
                      e.currentTarget.style.transform = 'translateY(-2px)'
                      e.currentTarget.style.boxShadow = '0 4px 12px rgba(76, 175, 80, 0.4)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = '#4CAF50'
                      e.currentTarget.style.transform = 'translateY(0)'
                      e.currentTarget.style.boxShadow = '0 2px 8px rgba(76, 175, 80, 0.3)'
                    }}
                  >
                    🎁 Попробовать бесплатно (первый урок)
                  </button>
                </div>
              )
            }
          }
          
          // Для купленных курсов или бесплатных курсов
          if (!(isPurchased || course.price === 0)) {
            return null
          }
          // Находим первый непройденный урок
          const firstUncompletedLesson = course.lessons.find((lesson) => {
            if (!progress || !progress.lessons || progress.lessons.length === 0) {
              // Если прогресса нет - возвращаем первый урок
              return true
            }
            const lessonProgress = progress.lessons.find(l => l.id === lesson.id)
            return !lessonProgress || !lessonProgress.completed
          })

          // Проверяем, все ли уроки пройдены
          const allLessonsCompleted = progress && progress.lessons && progress.lessons.length > 0 && 
            course.lessons.every((lesson) => {
              const lessonProgress = progress.lessons.find(l => l.id === lesson.id)
              return lessonProgress && lessonProgress.completed
            })

          // Определяем текст кнопки и урок для перехода
          let buttonText = 'Приступить к курсу'
          let targetLesson = course.lessons[0] // По умолчанию первый урок

          if (progress && progress.completed_lessons > 0) {
            if (allLessonsCompleted) {
              buttonText = 'Повторить курс'
              targetLesson = course.lessons[0] // Начинаем с первого урока
            } else if (firstUncompletedLesson) {
              buttonText = 'Продолжить обучение'
              targetLesson = firstUncompletedLesson
            }
          }

          return (
            <div style={{ marginTop: '20px' }}>
              <button
                onClick={() => navigate(`/lessons/${targetLesson.id}`)}
                style={{
                  width: '100%',
                  padding: '15px 20px',
                  backgroundColor: '#e91e63',
                  color: 'white',
                  border: 'none',
                  borderRadius: '12px',
                  fontSize: '16px',
                  fontWeight: 'bold',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  boxShadow: '0 2px 8px rgba(233, 30, 99, 0.3)'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#c2185b'
                  e.currentTarget.style.transform = 'translateY(-2px)'
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(233, 30, 99, 0.4)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#e91e63'
                  e.currentTarget.style.transform = 'translateY(0)'
                  e.currentTarget.style.boxShadow = '0 2px 8px rgba(233, 30, 99, 0.3)'
                }}
              >
                {buttonText}
              </button>
            </div>
          )
        })()}
      </div>

      {/* Список уроков */}
      <div className="course-lessons">
        <h2>📖 Уроки</h2>
        {!isPurchased && course.price > 0 && (
          <div className="course-locked" style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#fff3cd', borderRadius: '8px', border: '1px solid #ffc107' }}>
            <p style={{ margin: '0 0 10px 0', fontWeight: 'bold' }}>🔒 Для доступа ко всем урокам необходимо купить курс</p>
            <p className="preview-note" style={{ color: '#4CAF50', fontWeight: 'bold', margin: 0 }}>
              ✨ Первый урок доступен бесплатно для ознакомления!
            </p>
          </div>
        )}
        {course.lessons.length > 0 ? (
          <div className="lessons-list">
            {course.lessons.map((lesson) => {
              const lessonProgress = progress?.lessons.find(l => l.id === lesson.id)
              const isFirstLesson = lesson.order === 1
              const isAccessible = isPurchased || course.price === 0 || isFirstLesson
              
              // Нормализуем урок - НЕ используем spread оператор
              const normalizedLesson = {
                id: typeof lesson.id === 'number' && !isNaN(lesson.id) ? lesson.id : 0,
                title: typeof lesson.title === 'string' ? lesson.title : 'Без названия',
                order: typeof lesson.order === 'number' && !isNaN(lesson.order) ? lesson.order : 0,
                video_duration: typeof lesson.video_duration === 'number' && !isNaN(lesson.video_duration) && lesson.video_duration > 0 ? lesson.video_duration : undefined,
                is_free: lesson.is_free === true || isFirstLesson,
                completed: lessonProgress?.completed === true
              }
              
              return (
                <div key={normalizedLesson.id} style={{ position: 'relative' }}>
                  {!isAccessible && (
                    <div style={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      bottom: 0,
                      backgroundColor: 'rgba(0, 0, 0, 0.5)',
                      borderRadius: '8px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      zIndex: 10,
                      pointerEvents: 'none'
                    }}>
                      <span style={{ color: 'white', fontWeight: 'bold', fontSize: '14px' }}>🔒</span>
                    </div>
                  )}
                  {isFirstLesson && !isPurchased && course.price > 0 && (
                    <div style={{
                      position: 'absolute',
                      top: '5px',
                      right: '5px',
                      backgroundColor: '#4CAF50',
                      color: 'white',
                      padding: '2px 8px',
                      borderRadius: '12px',
                      fontSize: '11px',
                      fontWeight: 'bold',
                      zIndex: 11
                    }}>
                      БЕСПЛАТНО
                    </div>
                  )}
                  <LessonItem
                    lesson={normalizedLesson}
                    courseId={course.id}
                  />
                </div>
              )
            })}
          </div>
        ) : (
          <p>Уроков пока нет</p>
        )}
      </div>

      {/* Секция отзывов */}
      <ReviewsSection courseId={course.id} />
    </div>
  )
}

export default CoursePage

