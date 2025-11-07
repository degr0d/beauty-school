/**
 * Главная страница
 * Топ курсов + список категорий
 */

import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { coursesApi, accessApi, type Course, type AccessStatus } from '../api/client'
import CourseCard from '../components/CourseCard'
import AccessBlocked from '../components/AccessBlocked'

const MainPage = () => {
  const navigate = useNavigate()
  const [topCourses, setTopCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(true)
  const [accessStatus, setAccessStatus] = useState<AccessStatus | null>(null)
  const [checkingAccess, setCheckingAccess] = useState(true)
  const [accessError, setAccessError] = useState(false)

  useEffect(() => {
    checkAccess()
    loadTopCourses()
  }, [])

  const checkAccess = async () => {
    try {
      console.log('🔍 Проверка доступа...')
      const response = await accessApi.checkAccess()
      console.log('✅ Доступ получен:', response.data)
      setAccessStatus(response.data)
      setAccessError(false)
    } catch (error: any) {
      console.error('❌ Ошибка проверки доступа:', error)
      console.error('Детали ошибки:', error.response?.data || error.message)
      // Если ошибка - показываем контент без блокировки (fallback)
      // Это может быть проблема с API, но пользователь должен видеть что-то
      setAccessError(true)
      // Устанавливаем доступ, чтобы не блокировать контент
      setAccessStatus({ has_access: true, purchased_courses_count: 0, total_payments: 0 })
    } finally {
      setCheckingAccess(false)
      console.log('✅ Проверка доступа завершена, checkingAccess:', false)
    }
  }

  const loadTopCourses = async () => {
    try {
      console.log('📚 Загрузка топ курсов...')
      const response = await coursesApi.getAll({ is_top: true })
      // Гарантируем что это массив
      const rawCourses = Array.isArray(response.data) ? response.data : []
      // Нормализуем все курсы - гарантируем что все поля это примитивы
      const courses = rawCourses.map(course => ({
        id: typeof course?.id === 'number' && !isNaN(course.id) ? course.id : 0,
        title: typeof course?.title === 'string' ? course.title : 'Без названия',
        description: typeof course?.description === 'string' ? course.description : '',
        category: typeof course?.category === 'string' ? course.category : '',
        cover_image_url: typeof course?.cover_image_url === 'string' && course.cover_image_url.trim() !== '' ? course.cover_image_url : undefined,
        is_top: course?.is_top === true,
        price: typeof course?.price === 'number' && !isNaN(course.price) ? course.price : 0,
        duration_hours: typeof course?.duration_hours === 'number' && !isNaN(course.duration_hours) && course.duration_hours > 0 ? course.duration_hours : undefined
      }))
      setTopCourses(courses)
    } catch (error: any) {
      console.error('❌ Ошибка загрузки топ курсов:', error)
      console.error('Детали ошибки:', error.response?.data || error.message)
      // Устанавливаем пустой массив, чтобы не ломать рендер
      setTopCourses([])
    } finally {
      setLoading(false)
      console.log('✅ Загрузка курсов завершена, loading:', false)
    }
  }
  
  const handleViewCourses = () => {
    navigate('/courses')
  }

  const categories = [
    { id: 'manicure', label: '💅 Маникюр', emoji: '💅' },
    { id: 'pedicure', label: '🦶 Педикюр', emoji: '🦶' },
    { id: 'eyelashes', label: '👁 Ресницы', emoji: '👁' },
    { id: 'eyebrows', label: '🎨 Брови', emoji: '🎨' },
    { id: 'podology', label: '🩺 Подология', emoji: '🩺' },
    { id: 'marketing', label: '📢 Маркетинг', emoji: '📢' },
    { id: 'business', label: '💼 Своё дело', emoji: '💼' },
  ]

  // Добавляем таймаут для загрузки - если слишком долго, показываем контент
  useEffect(() => {
    const timeout = setTimeout(() => {
      if (checkingAccess || loading) {
        console.warn('⚠️ Загрузка слишком долгая, показываем контент')
        setCheckingAccess(false)
        setLoading(false)
        // Если accessStatus еще не установлен - устанавливаем fallback
        if (!accessStatus) {
          setAccessStatus({ has_access: true, purchased_courses_count: 0, total_payments: 0 })
        }
      }
    }, 5000) // 5 секунд таймаут

    return () => clearTimeout(timeout)
  }, [checkingAccess, loading, accessStatus])

  // Убрано логирование объектов - может вызывать проблемы

  // Если нет доступа и нет ошибки - показываем блокировку
  if (!accessError && accessStatus && !accessStatus.has_access) {
    console.log('🔒 Нет доступа, показываем блокировку')
    return <AccessBlocked onViewCourses={handleViewCourses} />
  }
  
  // ВСЕГДА показываем контент (даже если загрузка)
  // Категории всегда видны, курсы показываются когда загрузятся
  // УБИРАЕМ проверку checkingAccess - она блокирует рендер
  console.log('✅ Показываем контент (категории всегда видны)')
  return (
    <div className="main-page">
      {/* Топ курсов */}
      {topCourses.length > 0 ? (
        <section className="top-courses">
          <h2>🔥 Топ курсов месяца</h2>
          <div className="courses-grid">
            {topCourses.map((course) => (
              <CourseCard key={course.id} course={course} />
            ))}
          </div>
        </section>
      ) : loading ? (
        <section className="top-courses">
          <h2>🔥 Топ курсов месяца</h2>
          <div className="loading">Загрузка курсов...</div>
        </section>
      ) : null}

      {/* Категории - ВСЕГДА показываем */}
      <section className="categories">
        <h2>📚 Категории</h2>
        <div className="categories-grid">
          {categories.map((category) => (
            <Link
              key={category.id}
              to={`/courses?category=${category.id}`}
              className="category-card"
            >
              <span className="category-emoji">{category.emoji}</span>
              <span className="category-label">
                {category.label.replace(/^\S+ /, '')}
              </span>
            </Link>
          ))}
        </div>
      </section>
    </div>
  )
}

export default MainPage

