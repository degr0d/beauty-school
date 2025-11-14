/**
 * Главная страница
 * Топ курсов + список категорий
 */

import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { coursesApi, accessApi, challengesApi, type Course, type AccessStatus, type Challenge } from '../api/client'
import CourseCard from '../components/CourseCard'
import AccessBlocked from '../components/AccessBlocked'
import SkeletonLoader from '../components/SkeletonLoader'

const MainPage = () => {
  const navigate = useNavigate()
  const [topCourses, setTopCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(true)
  const [accessStatus, setAccessStatus] = useState<AccessStatus | null>(null)
  const [checkingAccess, setCheckingAccess] = useState(true)
  const [accessError, setAccessError] = useState(false)
  const [challenges, setChallenges] = useState<Challenge[]>([])

  useEffect(() => {
    checkAccess()
    loadTopCourses()
    loadChallenges()
  }, [])

  const checkAccess = async () => {
    try {
      console.log('🔍 Проверка доступа...')
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

  const loadChallenges = async () => {
    try {
      const response = await challengesApi.getAll()
      const rawChallenges = Array.isArray(response.data) ? response.data : []
      // Берем только первые 3 активных челленджа
      const activeChallenges = rawChallenges
        .filter((ch: Challenge) => ch.is_active)
        .slice(0, 3)
      setChallenges(activeChallenges)
    } catch (error) {
      console.error('Ошибка загрузки челленджей:', error)
      setChallenges([])
    }
  }

  const handleJoinChallenge = async (challengeId: number) => {
    try {
      await challengesApi.join(challengeId)
      // Перезагружаем челленджи
      await loadChallenges()
      if (window.Telegram?.WebApp) {
        window.Telegram.WebApp.showAlert('Вы присоединились к челленджу!')
      }
    } catch (error: any) {
      console.error('Ошибка присоединения к челленджу:', error)
      const errorMessage = error.response?.data?.detail || 'Не удалось присоединиться к челленджу'
      if (window.Telegram?.WebApp) {
        window.Telegram.WebApp.showAlert(`Ошибка: ${errorMessage}`)
      } else {
        alert(`Ошибка: ${errorMessage}`)
      }
    }
  }

  const getConditionText = (challenge: Challenge) => {
    switch (challenge.condition_type) {
      case 'complete_lessons':
        return `Пройдите ${challenge.condition_value} уроков`
      case 'complete_courses':
        return `Завершите ${challenge.condition_value} курсов`
      case 'earn_points':
        return `Заработайте ${challenge.condition_value} баллов`
      default:
        return `Выполните условие: ${challenge.condition_type}`
    }
  }

  const getProgressPercent = (challenge: Challenge) => {
    if (!challenge.user_progress) return 0
    return Math.min((challenge.user_progress / challenge.condition_value) * 100, 100)
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
          <div className="courses-grid">
            <SkeletonLoader type="card" count={3} />
          </div>
        </section>
      ) : null}

      {/* Челленджи */}
      {challenges.length > 0 && (
        <section className="challenges-section" style={{ marginTop: '30px', marginBottom: '30px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h2>🎯 Челленджи</h2>
            <Link
              to="/challenges"
              style={{
                fontSize: '14px',
                color: '#e91e63',
                textDecoration: 'none',
                fontWeight: 'bold'
              }}
            >
              Все челленджи →
            </Link>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            {challenges.map((challenge) => {
              const progressPercent = getProgressPercent(challenge)
              const isExpired = challenge.end_date && new Date(challenge.end_date) < new Date()
              
              return (
                <div
                  key={challenge.id}
                  style={{
                    padding: '15px',
                    backgroundColor: challenge.user_completed ? '#e8f5e9' : '#f9f9f9',
                    borderRadius: '12px',
                    border: challenge.user_completed ? '2px solid #4caf50' : '1px solid #e0e0e0'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px', marginBottom: '10px' }}>
                    <div style={{
                      width: '50px',
                      height: '50px',
                      borderRadius: '8px',
                      backgroundColor: '#e91e63',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '24px',
                      flexShrink: 0
                    }}>
                      🎯
                    </div>
                    
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '5px' }}>
                        <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 'bold', lineHeight: '1.3' }}>
                          {challenge.title}
                        </h3>
                        {challenge.user_completed && (
                          <span style={{
                            padding: '2px 8px',
                            backgroundColor: '#4caf50',
                            color: 'white',
                            borderRadius: '8px',
                            fontSize: '10px',
                            fontWeight: 'bold',
                            whiteSpace: 'nowrap',
                            marginLeft: '8px'
                          }}>
                            ✅
                          </span>
                        )}
                      </div>
                      
                      <p style={{ margin: '0 0 8px 0', color: '#666', fontSize: '12px', lineHeight: '1.4' }}>
                        {challenge.description}
                      </p>
                      
                      <div style={{ fontSize: '12px', color: '#666', marginBottom: '8px' }}>
                        <div>🎯 {getConditionText(challenge)}</div>
                        <div>💎 Награда: {challenge.points_reward} баллов</div>
                      </div>
                    </div>
                  </div>

                  {/* Прогресс */}
                  {challenge.user_joined && (
                    <div style={{ marginTop: '10px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px', fontSize: '12px' }}>
                        <span>Прогресс:</span>
                        <span style={{ fontWeight: 'bold' }}>
                          {challenge.user_progress || 0} / {challenge.condition_value}
                        </span>
                      </div>
                      <div style={{
                        width: '100%',
                        height: '6px',
                        backgroundColor: '#e0e0e0',
                        borderRadius: '3px',
                        overflow: 'hidden'
                      }}>
                        <div
                          style={{
                            width: `${progressPercent}%`,
                            height: '100%',
                            backgroundColor: challenge.user_completed ? '#4caf50' : '#e91e63',
                            transition: 'width 0.3s ease'
                          }}
                        />
                      </div>
                    </div>
                  )}

                  {/* Кнопка присоединения */}
                  {!challenge.user_joined && !isExpired && challenge.is_active && (
                    <button
                      onClick={() => handleJoinChallenge(challenge.id)}
                      style={{
                        marginTop: '10px',
                        width: '100%',
                        padding: '10px 16px',
                        backgroundColor: '#e91e63',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        fontSize: '14px',
                        fontWeight: 'bold',
                        cursor: 'pointer'
                      }}
                    >
                      Присоединиться
                    </button>
                  )}
                </div>
              )
            })}
          </div>
        </section>
      )}

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

