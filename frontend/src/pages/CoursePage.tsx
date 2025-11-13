/**
 * Страница детального просмотра курса
 */

import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { coursesApi, progressApi, paymentApi, type CourseDetail, type CourseProgress } from '../api/client'
import LessonItem from '../components/LessonItem'
import ProgressBar from '../components/ProgressBar'

const CoursePage = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
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

        {/* Кнопка "Приступить к курсу" / "Продолжить" */}
        {(isPurchased || course.price === 0) && course.lessons.length > 0 && (() => {
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
                  // Нормализуем урок - НЕ используем spread оператор
                  const normalizedLesson = {
                    id: typeof lesson.id === 'number' && !isNaN(lesson.id) ? lesson.id : 0,
                    title: typeof lesson.title === 'string' ? lesson.title : 'Без названия',
                    order: typeof lesson.order === 'number' && !isNaN(lesson.order) ? lesson.order : 0,
                    video_duration: typeof lesson.video_duration === 'number' && !isNaN(lesson.video_duration) && lesson.video_duration > 0 ? lesson.video_duration : undefined,
                    is_free: lesson.is_free === true,
                    completed: lessonProgress?.completed === true
                  }
                  return (
                    <LessonItem
                      key={normalizedLesson.id}
                      lesson={normalizedLesson}
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

