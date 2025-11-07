/**
 * Страница профиля пользователя
 * Простое отображение ФИО и номера телефона из бота
 */

import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { profileApi, accessApi, coursesApi, type Profile, type AccessStatus } from '../api/client'
import ProgressBar from '../components/ProgressBar'

type ProfileStatus = 'loading' | 'not_registered' | 'not_paid' | 'paid'

type CourseWithProgress = {
  id: number
  title: string
  description: string
  category: string
  cover_image_url?: string
  progress: {
    total_lessons: number
    completed_lessons: number
    progress_percent: number
    purchased_at: string | null
    is_completed: boolean
  }
}

const ProfilePage = () => {
  const navigate = useNavigate()
  const [profile, setProfile] = useState<Profile | null>(null)
  const [, setAccessStatus] = useState<AccessStatus | null>(null)
  const [status, setStatus] = useState<ProfileStatus>('loading')
  const [myCourses, setMyCourses] = useState<CourseWithProgress[]>([])
  const [loadingCourses, setLoadingCourses] = useState(false)

  useEffect(() => {
    loadProfile()
  }, [])

  useEffect(() => {
    if (status === 'paid' && profile) {
      loadMyCourses()
    }
  }, [status, profile])

  const loadProfile = async () => {
    try {
      const profileResponse = await profileApi.get()
      const rawProfile = profileResponse.data
      
      if (rawProfile) {
        // Нормализуем профиль - только ФИО и телефон
        const normalizedProfile: Profile = {
          id: typeof rawProfile.id === 'number' && !isNaN(rawProfile.id) ? rawProfile.id : 0,
          telegram_id: typeof rawProfile.telegram_id === 'number' && !isNaN(rawProfile.telegram_id) ? rawProfile.telegram_id : 0,
          username: rawProfile.username && typeof rawProfile.username === 'string' && rawProfile.username.trim() !== '' ? rawProfile.username : undefined,
          full_name: typeof rawProfile.full_name === 'string' && rawProfile.full_name.trim() !== '' ? rawProfile.full_name : 'Пользователь',
          phone: typeof rawProfile.phone === 'string' && rawProfile.phone.trim() !== '' ? rawProfile.phone : 'не указан',
          email: undefined,
          city: undefined,
          points: typeof rawProfile.points === 'number' && !isNaN(rawProfile.points) ? rawProfile.points : 0,
          created_at: typeof rawProfile.created_at === 'string' ? rawProfile.created_at : new Date().toISOString()
        }
        setProfile(normalizedProfile)
      }

      // Проверяем доступ
      try {
        const accessResponse = await accessApi.checkAccess()
        const rawAccess = accessResponse.data
        // Нормализуем accessStatus - гарантируем что все поля это примитивы
        if (rawAccess) {
          const normalizedAccess: AccessStatus = {
            has_access: rawAccess.has_access === true,
            purchased_courses_count: typeof rawAccess.purchased_courses_count === 'number' && !isNaN(rawAccess.purchased_courses_count) ? rawAccess.purchased_courses_count : 0,
            total_payments: typeof rawAccess.total_payments === 'number' && !isNaN(rawAccess.total_payments) ? rawAccess.total_payments : 0
          }
          setAccessStatus(normalizedAccess)
          
          if (normalizedAccess.has_access) {
            setStatus('paid')
          } else {
            setStatus('not_paid')
          }
        }
      } catch (error: any) {
        if (error.response?.status === 404) {
          setStatus('not_registered')
        } else {
          setStatus('not_paid')
        }
      }
    } catch (error: any) {
      console.error('Ошибка загрузки профиля:', error)
      if (error.response?.status === 404) {
        setStatus('not_registered')
      } else {
        setStatus('not_paid')
      }
    }
  }

  const loadMyCourses = async () => {
    try {
      setLoadingCourses(true)
      const response = await coursesApi.getMy()
      const courses = Array.isArray(response.data) ? response.data : []
      
      // Нормализуем курсы
      const safeCourses = courses.map(course => {
        const normalizedCourse: CourseWithProgress = {
          id: typeof course?.id === 'number' && !isNaN(course.id) ? course.id : 0,
          title: typeof course?.title === 'string' ? course.title : 'Без названия',
          description: typeof course?.description === 'string' ? course.description : '',
          category: typeof course?.category === 'string' ? course.category : '',
          cover_image_url: typeof course?.cover_image_url === 'string' && course.cover_image_url.trim() !== '' ? course.cover_image_url : undefined,
          progress: {
            total_lessons: typeof course?.progress?.total_lessons === 'number' && !isNaN(course.progress.total_lessons) ? course.progress.total_lessons : 0,
            completed_lessons: typeof course?.progress?.completed_lessons === 'number' && !isNaN(course.progress.completed_lessons) ? course.progress.completed_lessons : 0,
            progress_percent: typeof course?.progress?.progress_percent === 'number' && !isNaN(course.progress.progress_percent) ? Math.min(Math.max(course.progress.progress_percent, 0), 100) : 0,
            purchased_at: course?.progress?.purchased_at && typeof course.progress.purchased_at === 'string' && course.progress.purchased_at.trim() !== '' ? course.progress.purchased_at : null,
            is_completed: course?.progress?.is_completed === true
          }
        }
        return normalizedCourse
      })
      setMyCourses(safeCourses)
    } catch (error: any) {
      console.error('Ошибка загрузки курсов:', error)
      setMyCourses([])
    } finally {
      setLoadingCourses(false)
    }
  }

  if (status === 'loading') {
    return (
      <div className="profile-page">
        <div className="loading">Загрузка...</div>
      </div>
    )
  }

  if (status === 'not_registered') {
    return (
      <div className="profile-page">
        <div className="error">
          <h2>❌ Вы не зарегистрированы</h2>
          <p>Пожалуйста, зарегистрируйтесь через бота, чтобы получить доступ к платформе.</p>
          <button 
            onClick={() => navigate('/courses')}
            style={{ marginTop: '20px', padding: '10px 20px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
          >
            Вернуться к курсам
          </button>
        </div>
      </div>
    )
  }

  if (status === 'not_paid') {
    return (
      <div className="profile-page">
        <div className="error">
          <h2>🔒 Доступ ограничен</h2>
          <p>Для доступа к платформе необходимо приобрести хотя бы один курс.</p>
          {profile !== null && (
            <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f5f5f5', borderRadius: '8px' }}>
              <h3>Ваш профиль:</h3>
              <p><strong>Имя:</strong> {String(profile.full_name || 'Не указано')}</p>
              <p><strong>Телефон:</strong> {String(profile.phone || 'Не указан')}</p>
            </div>
          )}
          <button 
            onClick={() => navigate('/courses')}
            style={{ marginTop: '20px', padding: '10px 20px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
          >
            Выбрать курс
          </button>
        </div>
      </div>
    )
  }

  // status === 'paid' - показываем профиль
  if (!profile) {
    return <div className="loading">Загрузка профиля...</div>
  }

  return (
    <div className="profile-page">
      <h1>👤 Мой профиль</h1>

      {/* Основная информация */}
      <div className="profile-card">
        <div className="profile-avatar">
          {(() => {
            try {
              const name = profile.full_name
              if (name && typeof name === 'string' && name.length > 0) {
                const firstChar = name.charAt(0).toUpperCase()
                return firstChar
              }
              return '?'
            } catch (e) {
              return '?'
            }
          })()}
        </div>

        <div className="profile-info">
          <h2>{String(profile.full_name || 'Пользователь')}</h2>
          
          {profile.username && typeof profile.username === 'string' && profile.username.trim() !== '' && (
            <p className="username">@{String(profile.username)}</p>
          )}
          
          <p className="phone">📞 {String(profile.phone || 'не указан')}</p>
        </div>
      </div>

      {/* Баллы */}
      <div className="profile-stats">
        <div className="stat-card">
          <div className="stat-label">Баллы</div>
          <div className="stat-value">{typeof profile.points === 'number' ? profile.points : 0}</div>
        </div>
      </div>

      {/* Мои курсы */}
      <div className="profile-courses">
        <h3>📚 Мои курсы</h3>
        {loadingCourses ? (
          <div className="loading">Загрузка курсов...</div>
        ) : myCourses.length > 0 ? (
          <div className="courses-list">
            {myCourses.map((course) => {
              if (!course || typeof course !== 'object' || Array.isArray(course)) {
                return null
              }
              
              const courseId = typeof course.id === 'number' && !isNaN(course.id) ? course.id : 0
              const courseTitle = typeof course.title === 'string' ? course.title : 'Без названия'
              const courseDescription = typeof course.description === 'string' ? course.description : ''
              
              let progress: {
                total_lessons: number
                completed_lessons: number
                progress_percent: number
                purchased_at: string | null
                is_completed: boolean
              }
              
              if (course.progress && typeof course.progress === 'object' && !Array.isArray(course.progress)) {
                progress = {
                  total_lessons: typeof course.progress.total_lessons === 'number' && !isNaN(course.progress.total_lessons) ? course.progress.total_lessons : 0,
                  completed_lessons: typeof course.progress.completed_lessons === 'number' && !isNaN(course.progress.completed_lessons) ? course.progress.completed_lessons : 0,
                  progress_percent: typeof course.progress.progress_percent === 'number' && !isNaN(course.progress.progress_percent) ? Math.min(Math.max(course.progress.progress_percent, 0), 100) : 0,
                  purchased_at: course.progress.purchased_at && typeof course.progress.purchased_at === 'string' && course.progress.purchased_at.trim() !== '' ? String(course.progress.purchased_at) : null,
                  is_completed: course.progress.is_completed === true
                }
              } else {
                progress = {
                  total_lessons: 0,
                  completed_lessons: 0,
                  progress_percent: 0,
                  purchased_at: null,
                  is_completed: false
                }
              }
              
              return (
                <div 
                  key={courseId} 
                  className="course-item"
                  onClick={() => navigate(`/courses/${courseId}`)}
                  style={{
                    padding: '15px',
                    marginBottom: '15px',
                    backgroundColor: '#f9f9f9',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    border: '1px solid #e0e0e0'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                    <div style={{ flex: 1 }}>
                      <h4 style={{ margin: '0 0 5px 0', fontSize: '16px', fontWeight: 'bold' }}>
                        {courseTitle}
                      </h4>
                      <p style={{ margin: '0', fontSize: '14px', color: '#666' }}>
                        {courseDescription}
                      </p>
                    </div>
                    {progress.is_completed && (
                      <span style={{ 
                        padding: '4px 8px', 
                        backgroundColor: '#28a745', 
                        color: 'white', 
                        borderRadius: '4px',
                        fontSize: '12px',
                        fontWeight: 'bold'
                      }}>
                        ✅ Завершен
                      </span>
                    )}
                  </div>
                  <div style={{ marginTop: '10px' }}>
                    <ProgressBar percent={progress.progress_percent} />
                    <p style={{ margin: '5px 0 0 0', fontSize: '12px', color: '#666' }}>
                      Пройдено: {progress.completed_lessons} / {progress.total_lessons} уроков
                      {progress.progress_percent > 0 && (
                        <span> ({progress.progress_percent}%)</span>
                      )}
                    </p>
                    {progress.purchased_at !== null && typeof progress.purchased_at === 'string' && progress.purchased_at.trim() !== '' && (
                      <p style={{ margin: '5px 0 0 0', fontSize: '12px', color: '#999' }}>
                        Куплен: {(() => {
                          try {
                            const date = new Date(progress.purchased_at)
                            if (isNaN(date.getTime())) return 'Не указано'
                            return date.toLocaleDateString('ru-RU')
                          } catch (e) {
                            return 'Не указано'
                          }
                        })()}
                      </p>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        ) : (
          <div className="empty-state">
            <p>У вас пока нет купленных курсов</p>
            <button 
              onClick={() => navigate('/courses')}
              style={{
                marginTop: '10px',
                padding: '10px 20px',
                backgroundColor: '#007bff',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Выбрать курс
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default ProfilePage
