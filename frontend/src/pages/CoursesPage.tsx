/**
 * Страница каталога курсов
 */

import { useEffect, useState, useCallback } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { coursesApi, accessApi, type Course, type AccessStatus } from '../api/client'
import CourseCard from '../components/CourseCard'

const CoursesPage = () => {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const category = searchParams.get('category')

  const [courses, setCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedCategory, setSelectedCategory] = useState<string | null>(category)
  const [accessStatus, setAccessStatus] = useState<AccessStatus | null>(null)
  const [checkingAccess, setCheckingAccess] = useState(true)

  const checkAccess = useCallback(async () => {
    try {
      console.log('🔍 [CoursesPage] Проверка доступа...')
      const response = await accessApi.checkAccess()
      const rawAccess = response.data
      // Нормализуем accessStatus - гарантируем что все поля это примитивы
      if (rawAccess) {
        const normalizedAccess: AccessStatus = {
          has_access: rawAccess.has_access === true,
          purchased_courses_count: typeof rawAccess.purchased_courses_count === 'number' && !isNaN(rawAccess.purchased_courses_count) ? rawAccess.purchased_courses_count : 0,
          total_payments: typeof rawAccess.total_payments === 'number' && !isNaN(rawAccess.total_payments) ? rawAccess.total_payments : 0
        }
        setAccessStatus(normalizedAccess)
      }
    } catch (error: any) {
      console.error('❌ [CoursesPage] Ошибка проверки доступа:', error)
      console.error('Детали:', error.response?.status, error.response?.data)
      
      // Если 404 - пользователь не зарегистрирован, но это не значит что нет доступа
      // Для админов backend вернет has_access: true, так что если ошибка - вероятно проблема с API
      // Устанавливаем has_access: false только если точно знаем что пользователь не админ
      // Но лучше показывать контент, чтобы не блокировать админов
      setAccessStatus({ has_access: false, purchased_courses_count: 0, total_payments: 0 })
    } finally {
      setCheckingAccess(false)
    }
  }, [])

  const loadCourses = useCallback(async () => {
    try {
      setLoading(true)
      let rawCourses: any[] = []
      
      // Если есть доступ - сначала пробуем загрузить купленные курсы
      // Если купленных нет - показываем все курсы (для админов и новых пользователей)
      if (accessStatus?.has_access) {
        try {
          const response = await coursesApi.getMy()
          rawCourses = Array.isArray(response.data) ? response.data : []
          
          // Если купленных курсов нет - показываем все курсы
          // (это может быть админ или пользователь без курсов)
          if (rawCourses.length === 0) {
            console.log('📚 [CoursesPage] Купленных курсов нет, показываем все курсы')
            const params = selectedCategory ? { category: selectedCategory } : {}
            const allCoursesResponse = await coursesApi.getAll(params)
            rawCourses = Array.isArray(allCoursesResponse.data) ? allCoursesResponse.data : []
          }
        } catch (error) {
          // Если ошибка при загрузке купленных - показываем все курсы
          console.warn('⚠️ [CoursesPage] Ошибка загрузки купленных курсов, показываем все:', error)
          const params = selectedCategory ? { category: selectedCategory } : {}
          const allCoursesResponse = await coursesApi.getAll(params)
          rawCourses = Array.isArray(allCoursesResponse.data) ? allCoursesResponse.data : []
        }
      } else {
        // Если нет доступа - показываем все курсы для выбора
        const params = selectedCategory ? { category: selectedCategory } : {}
        const response = await coursesApi.getAll(params)
        rawCourses = Array.isArray(response.data) ? response.data : []
      }
      
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
      setCourses(courses)
    } catch (error) {
      console.error('Ошибка загрузки курсов:', error)
      // Устанавливаем пустой массив при ошибке
      setCourses([])
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
    { id: 'Маникюр и педикюр', label: 'Маникюр и педикюр' },
    { id: 'Ресницы и брови', label: 'Ресницы и брови' },
    { id: 'Своё дело', label: 'Своё дело' },
  ]

  if (checkingAccess || loading) {
    return <div className="loading">Загрузка...</div>
  }

  // Если нет доступа - показываем все курсы с призывом к оплате
  // НО: если accessStatus еще не загружен (null) - показываем контент (не блокируем)
  if (accessStatus && !accessStatus.has_access) {
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

  // Если есть доступ - показываем курсы (купленные или все, если купленных нет)
  // Если купленных нет, но есть доступ - это админ, показываем все курсы
  const hasPurchasedCourses = accessStatus?.purchased_courses_count && accessStatus.purchased_courses_count > 0
  
  return (
    <div className="courses-page">
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
      
      <h1>{hasPurchasedCourses ? '📚 Мои курсы' : '📚 Каталог курсов'}</h1>
      
      {/* Фильтр по категориям - показываем если нет купленных курсов или если выбрана категория */}
      {(!hasPurchasedCourses || selectedCategory) && (
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
      )}
      
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

