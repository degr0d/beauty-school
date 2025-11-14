/**
 * Страница профиля пользователя
 * Простое отображение ФИО и номера телефона из бота
 */

import { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { profileApi, accessApi, coursesApi, certificatesApi, favoritesApi, type Profile, type AccessStatus, type Certificate, type Course } from '../api/client'
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
  const [certificates, setCertificates] = useState<Certificate[]>([])
  const [loadingCertificates, setLoadingCertificates] = useState(false)
  const [favoriteCourses, setFavoriteCourses] = useState<Course[]>([])
  const [loadingFavorites, setLoadingFavorites] = useState(false)

  const loadFavorites = useCallback(async () => {
    try {
      setLoadingFavorites(true)
      console.log('❤️ [ProfilePage] Загрузка избранных курсов...')
      const response = await favoritesApi.getAll()
      const rawFavorites = Array.isArray(response.data) ? response.data : []
      console.log('❤️ [ProfilePage] Получено избранных курсов:', rawFavorites.length, rawFavorites)
      
      // Нормализуем курсы
      const normalizedFavorites = rawFavorites.map((course: any) => ({
        id: typeof course?.id === 'number' && !isNaN(course.id) ? course.id : 0,
        title: typeof course?.title === 'string' ? course.title : 'Без названия',
        description: typeof course?.description === 'string' ? course.description : '',
        category: typeof course?.category === 'string' ? course.category : '',
        cover_image_url: typeof course?.cover_image_url === 'string' && course.cover_image_url.trim() !== '' ? course.cover_image_url : undefined,
        is_top: course?.is_top === true,
        price: typeof course?.price === 'number' && !isNaN(course.price) ? course.price : 0,
        duration_hours: typeof course?.duration_hours === 'number' && !isNaN(course.duration_hours) && course.duration_hours > 0 ? course.duration_hours : undefined
      }))
      
      console.log('❤️ [ProfilePage] Нормализованные избранные курсы:', normalizedFavorites)
      setFavoriteCourses(normalizedFavorites)
    } catch (error: any) {
      console.error('❌ [ProfilePage] Ошибка загрузки избранных курсов:', error)
      console.error('   Детали:', error.response?.status, error.response?.data)
      setFavoriteCourses([])
    } finally {
      setLoadingFavorites(false)
    }
  }, [])

  const loadCertificates = useCallback(async () => {
    try {
      setLoadingCertificates(true)
      console.log('📜 [ProfilePage] Загрузка сертификатов...')
      const response = await certificatesApi.getAll()
      const rawCertificates = Array.isArray(response.data) ? response.data : []
      console.log('📜 [ProfilePage] Получено сертификатов:', rawCertificates.length, rawCertificates)
      
      // Нормализуем сертификаты
      const normalizedCertificates = rawCertificates.map((cert: any) => ({
        id: typeof cert.id === 'number' && !isNaN(cert.id) ? cert.id : 0,
        course_id: typeof cert.course_id === 'number' && !isNaN(cert.course_id) ? cert.course_id : 0,
        course_title: typeof cert.course_title === 'string' ? cert.course_title : '',
        certificate_url: typeof cert.certificate_url === 'string' ? cert.certificate_url : '',
        certificate_number: typeof cert.certificate_number === 'string' ? cert.certificate_number : '',
        issued_at: typeof cert.issued_at === 'string' ? cert.issued_at : new Date().toISOString()
      }))
      
      console.log('📜 [ProfilePage] Нормализованные сертификаты:', normalizedCertificates)
      setCertificates(normalizedCertificates)
    } catch (error: any) {
      console.error('❌ [ProfilePage] Ошибка загрузки сертификатов:', error)
      console.error('   Детали:', error.response?.status, error.response?.data)
      setCertificates([])
    } finally {
      setLoadingCertificates(false)
    }
  }, [])

  const loadMyCourses = useCallback(async () => {
    try {
      setLoadingCourses(true)
      console.log('📚 [ProfilePage] Загрузка курсов...')
      const response = await coursesApi.getMy()
      const courses = Array.isArray(response.data) ? response.data : []
      console.log('📚 [ProfilePage] Получено курсов:', courses.length, courses)
      
      // Нормализуем курсы
      const safeCourses = courses.map((course: any) => {
        const normalizedCourse: CourseWithProgress = {
          id: typeof course?.id === 'number' && !isNaN(course.id) ? course.id : 0,
          title: typeof course?.title === 'string' ? course.title : 'Без названия',
          description: typeof course?.description === 'string' ? course.description : '',
          category: typeof course?.category === 'string' ? course.category : '',
          cover_image_url: typeof course?.cover_image_url === 'string' && course.cover_image_url.trim() !== '' ? course.cover_image_url : undefined,
          progress: {
            total_lessons: typeof course?.progress?.total_lessons === 'number' && !isNaN(course.progress?.total_lessons) ? course.progress.total_lessons : 0,
            completed_lessons: typeof course?.progress?.completed_lessons === 'number' && !isNaN(course.progress?.completed_lessons) ? course.progress.completed_lessons : 0,
            progress_percent: typeof course?.progress?.progress_percent === 'number' && !isNaN(course.progress?.progress_percent) ? Math.min(Math.max(course.progress.progress_percent, 0), 100) : 0,
            purchased_at: (() => {
              const purchasedAt = course?.progress?.purchased_at
              if (!purchasedAt) return null
              if (typeof purchasedAt === 'string' && purchasedAt.trim() !== '') {
                return purchasedAt
              } else if (purchasedAt && typeof purchasedAt === 'object') {
                try {
                  const purchasedAtAny: any = purchasedAt
                  if (purchasedAtAny instanceof Date) {
                    return purchasedAtAny.toISOString()
                  } else if (typeof purchasedAtAny.toISOString === 'function') {
                    return purchasedAtAny.toISOString()
                  }
                } catch (e) {
                  console.warn('Ошибка преобразования purchased_at:', e)
                }
              }
              return null
            })(),
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
  }, [])

  const loadProfile = async () => {
    try {
      const currentDevId = localStorage.getItem('dev_telegram_id')
      console.log('📥 [ProfilePage] Загрузка профиля, текущий dev_telegram_id:', currentDevId)
      const profileResponse = await profileApi.get()
      const rawProfile = profileResponse.data
      console.log('📥 [ProfilePage] Получен профиль:', rawProfile)
      
      if (rawProfile) {
        // КРИТИЧЕСКИ ВАЖНО: Преобразуем ВСЕ поля в примитивы перед установкой в state
        // Это предотвращает React error #301 (Objects are not valid as a React child)
        
        // Безопасно преобразуем created_at - может быть объектом datetime
        let created_at_str: string
        try {
          if (!rawProfile.created_at) {
            created_at_str = new Date().toISOString()
          } else if (typeof rawProfile.created_at === 'string') {
            created_at_str = rawProfile.created_at
          } else if (typeof rawProfile.created_at === 'object') {
            // Если это объект datetime, пытаемся преобразовать
            const created_at: any = rawProfile.created_at
            if (created_at instanceof Date) {
              created_at_str = created_at.toISOString()
            } else if (created_at && typeof created_at.toISOString === 'function') {
              created_at_str = created_at.toISOString()
            } else {
              // Пытаемся преобразовать через JSON
              try {
                created_at_str = JSON.stringify(created_at)
              } catch {
                created_at_str = new Date().toISOString()
              }
            }
          } else {
            created_at_str = String(rawProfile.created_at)
          }
        } catch (e) {
          console.warn('Ошибка преобразования created_at:', e)
          created_at_str = new Date().toISOString()
        }
        
        // Нормализуем профиль - гарантируем что ВСЕ поля это примитивы (string, number, boolean, undefined)
        // НИКАКИХ объектов или массивов!
        const normalizedProfile: Profile = {
          id: typeof rawProfile.id === 'number' && !isNaN(rawProfile.id) ? rawProfile.id : 0,
          telegram_id: typeof rawProfile.telegram_id === 'number' && !isNaN(rawProfile.telegram_id) ? rawProfile.telegram_id : 0,
          username: rawProfile.username && typeof rawProfile.username === 'string' && rawProfile.username.trim() !== '' ? String(rawProfile.username).trim() : undefined,
          full_name: typeof rawProfile.full_name === 'string' && rawProfile.full_name.trim() !== '' ? String(rawProfile.full_name).trim() : 'Пользователь',
          phone: typeof rawProfile.phone === 'string' && rawProfile.phone.trim() !== '' ? String(rawProfile.phone).trim() : 'не указан',
          city: rawProfile.city && typeof rawProfile.city === 'string' && rawProfile.city.trim() !== '' ? String(rawProfile.city).trim() : undefined,
          points: typeof rawProfile.points === 'number' && !isNaN(rawProfile.points) ? Number(rawProfile.points) : 0,
          created_at: String(created_at_str) // Явно преобразуем в строку
        }
        
        // Дополнительная проверка: убеждаемся что в профиле нет объектов
        const profileKeys = Object.keys(normalizedProfile) as Array<keyof Profile>
        for (const key of profileKeys) {
          const value = normalizedProfile[key]
          if (value !== null && value !== undefined && typeof value === 'object') {
            console.error(`❌ КРИТИЧЕСКАЯ ОШИБКА: Поле ${key} является объектом!`, value)
            // Преобразуем объект в строку
            try {
              (normalizedProfile as any)[key] = JSON.stringify(value)
            } catch {
              (normalizedProfile as any)[key] = String(value)
            }
          }
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

  useEffect(() => {
    loadProfile()
    
    // Слушаем изменения dev_telegram_id в localStorage для автоматического обновления
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'dev_telegram_id') {
        console.log('🔄 [ProfilePage] dev_telegram_id изменен, перезагружаем профиль...')
        loadProfile()
      }
    }
    
    // Слушаем события storage (из других вкладок)
    window.addEventListener('storage', handleStorageChange)
    
    // Слушаем кастомное событие для обновления в той же вкладке
    const handleCustomStorageChange = () => {
      const currentId = localStorage.getItem('dev_telegram_id')
      console.log('🔄 [ProfilePage] dev_telegram_id изменен (custom event), перезагружаем профиль...', 'текущий ID:', currentId)
      // Небольшая задержка чтобы убедиться что localStorage обновился
      setTimeout(() => {
        loadProfile()
      }, 200)
    }
    
    window.addEventListener('dev_telegram_id_changed', handleCustomStorageChange)
    
    // Слушаем событие завершения курса для обновления сертификатов
    const handleCourseCompleted = () => {
      console.log('🎉 [ProfilePage] Курс завершен, обновляем сертификаты...')
      if (profile) {
        loadCertificates()
      }
    }
    window.addEventListener('course_completed', handleCourseCompleted)
    
    // Слушаем изменения избранного для обновления списка
    const handleFavoriteChanged = () => {
      console.log('❤️ [ProfilePage] Избранное изменено, обновляем список...')
      if (profile) {
        loadFavorites()
      }
    }
    window.addEventListener('favorite_changed', handleFavoriteChanged)
    
    return () => {
      window.removeEventListener('storage', handleStorageChange)
      window.removeEventListener('dev_telegram_id_changed', handleCustomStorageChange)
      window.removeEventListener('course_completed', handleCourseCompleted)
      window.removeEventListener('favorite_changed', handleFavoriteChanged)
    }
  }, [profile, loadCertificates, loadFavorites])

  useEffect(() => {
    // Загружаем курсы если:
    // 1. Пользователь имеет доступ (status === 'paid')
    // 2. Или если есть профиль (для админов и пользователей с прогрессом)
    if ((status === 'paid' || profile) && profile) {
      loadMyCourses()
      loadCertificates()
      loadFavorites()
    }
  }, [status, profile?.id, loadMyCourses, loadCertificates, loadFavorites]) // Добавляем функции в зависимости

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
        
        {/* Кнопка лидборда */}
        <div style={{ marginTop: '20px', marginBottom: '20px' }}>
          <button
            onClick={() => navigate('/leaderboard')}
            style={{
              width: '100%',
              padding: '12px 20px',
              backgroundColor: '#e91e63',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: 'bold',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px'
            }}
          >
            🏆 Лидборд
          </button>
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
                  purchased_at: (() => {
                    const purchasedAt = course.progress.purchased_at
                    if (!purchasedAt) return null
                    // Безопасно преобразуем purchased_at - может быть объектом datetime
                    if (typeof purchasedAt === 'string' && purchasedAt.trim() !== '') {
                      return purchasedAt
                    } else if (purchasedAt && typeof purchasedAt === 'object') {
                      try {
                        const purchasedAtAny: any = purchasedAt
                        if (purchasedAtAny instanceof Date) {
                          return purchasedAtAny.toISOString()
                        } else if (typeof purchasedAtAny.toISOString === 'function') {
                          return purchasedAtAny.toISOString()
                        }
                      } catch (e) {
                        console.warn('Ошибка преобразования purchased_at:', e)
                      }
                    }
                    return null
                  })(),
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

      {/* Избранные курсы */}
      <div className="profile-favorites">
        <h3>❤️ Избранные курсы</h3>
        {loadingFavorites ? (
          <div className="loading">Загрузка избранных курсов...</div>
        ) : favoriteCourses.length > 0 ? (
          <div className="courses-list">
            {favoriteCourses.map((course) => {
              const courseId = typeof course.id === 'number' && !isNaN(course.id) ? course.id : 0
              const courseTitle = typeof course.title === 'string' ? course.title : 'Без названия'
              const courseDescription = typeof course.description === 'string' ? course.description : ''
              const coverImageUrl = typeof course.cover_image_url === 'string' && course.cover_image_url.trim() !== '' ? course.cover_image_url : undefined
              
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
                    border: '1px solid #e0e0e0',
                    display: 'flex',
                    gap: '15px'
                  }}
                >
                  {coverImageUrl && (
                    <img 
                      src={coverImageUrl} 
                      alt={courseTitle}
                      style={{
                        width: '80px',
                        height: '80px',
                        objectFit: 'cover',
                        borderRadius: '8px',
                        flexShrink: 0
                      }}
                    />
                  )}
                  <div style={{ flex: 1 }}>
                    <h4 style={{ margin: '0 0 5px 0', fontSize: '16px', fontWeight: 'bold' }}>
                      {courseTitle}
                    </h4>
                    <p style={{ margin: '0', fontSize: '14px', color: '#666' }}>
                      {courseDescription}
                    </p>
                    {course.duration_hours && (
                      <p style={{ margin: '5px 0 0 0', fontSize: '12px', color: '#999' }}>
                        ⏱ {course.duration_hours} ч
                      </p>
                    )}
                    {course.price > 0 && (
                      <p style={{ margin: '5px 0 0 0', fontSize: '14px', fontWeight: 'bold', color: '#e91e63' }}>
                        {course.price} ₽
                      </p>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        ) : (
          <div className="empty-state">
            <p>У вас пока нет избранных курсов</p>
            <p style={{ fontSize: '12px', color: '#999', marginTop: '5px' }}>
              Добавьте курсы в избранное, нажав на сердечко ❤️
            </p>
            <button 
              onClick={() => navigate('/courses')}
              style={{
                marginTop: '10px',
                padding: '10px 20px',
                backgroundColor: '#e91e63',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Перейти к каталогу
            </button>
          </div>
        )}
      </div>

      {/* Сертификаты */}
      <div className="profile-certificates">
        <h3>🏆 Мои сертификаты</h3>
        {loadingCertificates ? (
          <div className="loading">Загрузка сертификатов...</div>
        ) : certificates.length > 0 ? (
          <div className="certificates-list">
            {certificates.map((cert) => (
              <div key={cert.id} className="certificate-item" style={{
                padding: '15px',
                marginBottom: '15px',
                backgroundColor: '#f9f9f9',
                borderRadius: '8px',
                border: '1px solid #e0e0e0'
              }}>
                <h4 style={{ margin: '0 0 10px 0', color: '#333' }}>{cert.course_title}</h4>
                <p style={{ margin: '5px 0', fontSize: '12px', color: '#666' }}>
                  Номер: {cert.certificate_number}
                </p>
                {cert.issued_at && (
                  <p style={{ margin: '5px 0', fontSize: '12px', color: '#999' }}>
                    Выдан: {(() => {
                      try {
                        const date = new Date(cert.issued_at)
                        if (isNaN(date.getTime())) return 'Не указано'
                        return date.toLocaleDateString('ru-RU')
                      } catch (e) {
                        return 'Не указано'
                      }
                    })()}
                  </p>
                )}
                {cert.certificate_url && (
                  <a
                    href={cert.certificate_url.startsWith('http') ? cert.certificate_url : `${import.meta.env.VITE_API_URL || '/api'}${cert.certificate_url}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      display: 'inline-block',
                      marginTop: '10px',
                      padding: '8px 16px',
                      backgroundColor: '#e91e63',
                      color: 'white',
                      textDecoration: 'none',
                      borderRadius: '4px',
                      fontSize: '14px'
                    }}
                  >
                    📥 Скачать сертификат
                  </a>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <p>У вас пока нет сертификатов</p>
            <p style={{ fontSize: '12px', color: '#999', marginTop: '5px' }}>
              Завершите курс, чтобы получить сертификат
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default ProfilePage
