/**
 * Страница каталога курсов
 */

import { useEffect, useState, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import { coursesApi, accessApi, type Course, type AccessStatus } from '../api/client'
import CourseCard from '../components/CourseCard'

const CoursesPage = () => {
  const [searchParams] = useSearchParams()
  const category = searchParams.get('category')

  const [courses, setCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedCategory, setSelectedCategory] = useState<string | null>(category)
  const [accessStatus, setAccessStatus] = useState<AccessStatus | null>(null)
  const [checkingAccess, setCheckingAccess] = useState(true)

  const checkAccess = useCallback(async () => {
    try {
      const response = await accessApi.checkAccess()
      setAccessStatus(response.data)
    } catch (error) {
      console.error('Ошибка проверки доступа:', error)
      setAccessStatus({ has_access: false, purchased_courses_count: 0, total_payments: 0 })
    } finally {
      setCheckingAccess(false)
    }
  }, [])

  const loadCourses = useCallback(async () => {
    try {
      setLoading(true)
      // Если есть доступ - показываем только купленные курсы
      // Если нет - показываем все курсы для выбора
      if (accessStatus?.has_access) {
        const response = await coursesApi.getMy()
        setCourses(response.data)
      } else {
        const params = selectedCategory ? { category: selectedCategory } : {}
        const response = await coursesApi.getAll(params)
        setCourses(response.data)
      }
    } catch (error) {
      console.error('Ошибка загрузки курсов:', error)
    } finally {
      setLoading(false)
    }
  }, [accessStatus?.has_access, selectedCategory])

  useEffect(() => {
    checkAccess()
  }, [checkAccess])

  useEffect(() => {
    if (!checkingAccess) {
      loadCourses()
    }
  }, [checkingAccess, loadCourses])

  const categories = [
    { id: null, label: 'Все' },
    { id: 'manicure', label: 'Маникюр' },
    { id: 'pedicure', label: 'Педикюр' },
    { id: 'eyelashes', label: 'Ресницы' },
    { id: 'eyebrows', label: 'Брови' },
    { id: 'podology', label: 'Подология' },
    { id: 'marketing', label: 'Маркетинг' },
    { id: 'business', label: 'Своё дело' },
  ]

  if (checkingAccess || loading) {
    return <div className="loading">Загрузка...</div>
  }

  // Если нет доступа - показываем все курсы с призывом к оплате
  if (!accessStatus?.has_access) {
    return (
      <div className="courses-page">
        <div className="access-warning">
          <h2>🔒 Для доступа к платформе выберите и оплатите курс</h2>
          <p>После оплаты вы получите доступ ко всем материалам и функциям платформы.</p>
        </div>
        <h1>📚 Каталог курсов</h1>

      {/* Фильтр по категориям */}
      <div className="categories-filter">
        {categories.map((cat) => (
          <button
            key={cat.id || 'all'}
            className={`filter-btn ${selectedCategory === cat.id ? 'active' : ''}`}
            onClick={() => setSelectedCategory(cat.id)}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Список курсов */}
      {courses.length > 0 ? (
        <div className="courses-grid">
          {courses.map((course) => (
            <CourseCard key={course.id} course={course} />
          ))}
        </div>
      ) : (
        <div className="empty-state">
          <p>Курсов пока нет</p>
        </div>
      )}
        
        <div className="access-note">
          <p>💡 После оплаты любого курса вы получите доступ ко всем функциям платформы</p>
        </div>
      </div>
    )
  }

  // Если есть доступ - показываем купленные курсы
  return (
    <div className="courses-page">
      <h1>📚 Мои курсы</h1>
      
      {courses.length > 0 ? (
        <div className="courses-grid">
          {courses.map((course) => (
            <CourseCard key={course.id} course={course} />
          ))}
        </div>
      ) : (
        <div className="empty-state">
          <p>У вас пока нет купленных курсов</p>
          <p>Выберите курс из каталога, чтобы начать обучение</p>
        </div>
      )}
    </div>
  )
}

export default CoursesPage

