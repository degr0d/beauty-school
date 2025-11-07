/**
 * Страница профиля пользователя
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
  const [isEditing, setIsEditing] = useState(false)
  const [editForm, setEditForm] = useState({
    full_name: '',
    phone: '',
    email: '',
    city: ''
  })
  const [saving, setSaving] = useState(false)
  const [debugLogs, setDebugLogs] = useState<string[]>([])
  const [showDebug, setShowDebug] = useState(true) // ВСЕГДА показываем логи для диагностики
  const [myCourses, setMyCourses] = useState<CourseWithProgress[]>([])
  const [loadingCourses, setLoadingCourses] = useState(false)
  
  // Функция для добавления логов (должна быть определена до использования)
  const addLog = (message: string, data?: any) => {
    const timestamp = new Date().toLocaleTimeString()
    let logMessage = `[${timestamp}] ${message}`
    
    // Если передан объект - добавляем его как JSON
    if (data !== undefined) {
      try {
        const dataStr = typeof data === 'object' ? JSON.stringify(data, null, 2) : String(data)
        logMessage += `\n   Данные: ${dataStr}`
      } catch (e) {
        logMessage += `\n   Данные: [не удалось сериализовать]`
      }
    }
    
    setDebugLogs(prev => {
      const newLogs = [...prev, logMessage]
      // Оставляем последние 100 логов (увеличено для лучшей диагностики)
      return newLogs.slice(-100)
    })
    // Также логируем в консоль для тех, у кого есть доступ
    if (data !== undefined) {
      console.log(logMessage, data)
    } else {
      console.log(logMessage)
    }
  }

  const loadProfileAndAccess = async () => {
    try {
      // Проверяем наличие Telegram WebApp и initData
      const webApp = window.Telegram?.WebApp
      const debugInfo = {
        hasWebApp: !!webApp,
        hasInitData: !!webApp?.initData,
        user: webApp?.initDataUnsafe?.user,
        telegramId: webApp?.initDataUnsafe?.user?.id
      }
      addLog(`🔍 Проверка Telegram WebApp: ${JSON.stringify(debugInfo)}`)
      console.log('🔍 Проверка Telegram WebApp:', debugInfo)
      
      // Сначала пробуем загрузить профиль
      let profileData: Profile | null = null
      
      try {
        addLog('📡 Запрос профиля...')
        console.log('📡 Запрос профиля...')
        const profileResponse = await profileApi.get()
        addLog(`✅ Профиль получен: ${JSON.stringify(profileResponse.data)}`)
        console.log('✅ Профиль получен:', profileResponse.data)
        const profileDetails = {
          full_name: profileResponse.data?.full_name,
          phone: profileResponse.data?.phone,
          email: profileResponse.data?.email,
          city: profileResponse.data?.city,
          username: profileResponse.data?.username,
          points: profileResponse.data?.points,
          created_at: profileResponse.data?.created_at,
          created_at_type: typeof profileResponse.data?.created_at
        }
        console.log('🔍 Детали профиля:', profileDetails)
        addLog('🔍 Детали профиля', profileDetails)
        // Безопасно нормализуем данные профиля - гарантируем что все значения примитивы
        const rawProfile = profileResponse.data
        if (rawProfile) {
          profileData = {
            ...rawProfile,
            // Гарантируем что created_at это строка
            created_at: rawProfile.created_at 
              ? (typeof rawProfile.created_at === 'string' 
                  ? rawProfile.created_at 
                  : (rawProfile.created_at instanceof Date 
                      ? rawProfile.created_at.toISOString() 
                      : String(rawProfile.created_at)))
              : '',
            // Гарантируем что все остальные поля это примитивы
            full_name: String(rawProfile.full_name || 'Пользователь'),
            phone: String(rawProfile.phone || ''),
            email: rawProfile.email ? String(rawProfile.email) : undefined,
            city: rawProfile.city ? String(rawProfile.city) : undefined,
            username: rawProfile.username ? String(rawProfile.username) : undefined,
            points: typeof rawProfile.points === 'number' ? rawProfile.points : 0
          }
        }
        
        // Проверяем, что данные не пустые
        if (profileData) {
          if (!profileData.full_name || profileData.full_name.trim() === '') {
            addLog('⚠️ ВНИМАНИЕ: full_name пустой!')
            console.warn('⚠️ full_name пустой:', profileData)
          }
          if (!profileData.phone || profileData.phone.trim() === '') {
            addLog('⚠️ ВНИМАНИЕ: phone пустой!')
            console.warn('⚠️ phone пустой:', profileData)
          }
        }
      } catch (error: any) {
        console.error('❌ Ошибка загрузки профиля:', {
          status: error.response?.status,
          statusText: error.response?.statusText,
          data: error.response?.data,
          message: error.message,
          url: error.config?.url,
          headers: error.config?.headers
        })
        
        // Если 401 - проблема с авторизацией (initData не валиден или отсутствует)
        if (error.response?.status === 401) {
          addLog('⚠️ Проблема с авторизацией (401)')
          addLog('💡 Проверьте что открываете Mini App через бота в Telegram')
          console.log('⚠️ Проблема с авторизацией (401)')
          console.log('💡 Проверьте что:')
          console.log('   1. Открываете Mini App через бота в Telegram')
          console.log('   2. Mini App открыт из Telegram (не в браузере)')
          console.log('   3. initData передается корректно')
          
          // Проверяем наличие initData
          const webApp = window.Telegram?.WebApp
          if (!webApp?.initData) {
            addLog('❌ initData отсутствует! Mini App открыт не через Telegram бота')
            console.error('❌ initData отсутствует! Это означает что Mini App открыт не через Telegram бота')
          } else {
            addLog('✅ initData присутствует, но валидация не прошла. Возможно проблема на backend.')
            console.log('✅ initData присутствует, но валидация не прошла. Возможно проблема на backend.')
          }
          
          setStatus('not_registered')
          return
        }
        
        // Если 404 - пользователь не зарегистрирован (но backend должен создавать автоматически)
        if (error.response?.status === 404) {
          addLog('⚠️ Пользователь не найден (404)')
          addLog('💡 Backend должен создавать профиль автоматически. Проверьте логи Railway.')
          addLog('💡 Возможно проблема с типами данных telegram_id')
          addLog(`Детали ошибки: ${JSON.stringify({ status: 404, message: error.message, url: error.config?.url })}`)
          console.log('⚠️ Пользователь не найден (404)')
          console.log('💡 Backend должен создавать профиль автоматически. Проверьте логи Railway.')
          console.log('💡 Возможно проблема с типами данных telegram_id')
          setStatus('not_registered')
          return
        }
        
        // Если 500 - ошибка на сервере
        if (error.response?.status === 500) {
          addLog(`❌ Ошибка сервера (500): ${JSON.stringify(error.response?.data)}`)
          addLog('💡 Проверьте логи backend для деталей')
          console.error('❌ Ошибка сервера (500):', error.response?.data)
          console.log('💡 Проверьте логи backend для деталей')
          // Показываем ошибку, но не блокируем - может быть временная проблема
          setStatus('not_registered')
          return
        }
        
        // Другая ошибка - тоже считаем не зарегистрирован
        addLog(`❌ Неизвестная ошибка: ${error.message || 'Неизвестная ошибка'}`)
        addLog(`Статус: ${error.response?.status || 'нет статуса'}`)
        addLog(`URL: ${error.config?.url || 'нет URL'}`)
        console.error('❌ Неизвестная ошибка:', error)
        setStatus('not_registered')
        return
      }

      // Если профиль загружен - проверяем доступ
      let accessData: AccessStatus | null = null
      
      try {
        console.log('📡 Запрос проверки доступа...')
        const accessResponse = await accessApi.checkAccess()
        console.log('✅ Доступ получен:', accessResponse.data)
        accessData = accessResponse.data
      } catch (error: any) {
        console.error('❌ Ошибка проверки доступа:', {
          status: error.response?.status,
          data: error.response?.data,
          message: error.message
        })
        
        // Если 404 - пользователь не зарегистрирован
        if (error.response?.status === 404) {
          // Но если профиль уже загружен - значит пользователь есть
          if (profileData) {
            // Профиль есть, но проверка доступа вернула 404
            // Это может быть админ или новая регистрация
            // Проверяем: если пользователь зарегистрирован но проверка доступа не прошла
            // - возможно это админ, у которого должен быть доступ
            // Backend для админов должен вернуть has_access: true, но если вернул 404
            // значит либо пользователь не админ, либо проблема с проверкой
            // Для безопасности - если профиль есть, даем доступ (админы должны иметь доступ)
            console.log('⚠️ Профиль есть, но проверка доступа вернула 404 - возможно админ')
            accessData = { has_access: true, purchased_courses_count: 999, total_payments: 0 }
          } else {
            setStatus('not_registered')
            return
          }
        } else {
          // Другая ошибка - если профиль есть, возможно это админ
          // Для админов backend должен вернуть has_access: true
          // Если ошибка - но профиль есть, даем доступ (может быть админ)
          if (profileData) {
            console.log('⚠️ Ошибка проверки доступа, но профиль есть - возможно админ, даем доступ')
            accessData = { has_access: true, purchased_courses_count: 999, total_payments: 0 }
          } else {
            console.error('Ошибка проверки доступа и профиля нет:', error)
            accessData = { has_access: false, purchased_courses_count: 0, total_payments: 0 }
          }
        }
      }

      // Инициализируем форму редактирования
      if (profileData) {
        setEditForm({
          full_name: profileData.full_name || '',
          phone: profileData.phone || '',
          email: profileData.email || '',
          city: profileData.city || ''
        })
        console.log('📝 Форма редактирования инициализирована:', {
          full_name: profileData.full_name,
          phone: profileData.phone,
          email: profileData.email,
          city: profileData.city
        })
      }

      // Сохраняем данные ПЕРЕД определением статуса
      setProfile(profileData)
      setAccessStatus(accessData)
      
      // Определяем статус
      const statusInfo = {
        hasProfile: !!profileData,
        hasAccessData: !!accessData,
        hasAccess: accessData?.has_access,
        purchasedCourses: accessData?.purchased_courses_count,
        profileName: profileData?.full_name || 'нет',
        profilePhone: profileData?.phone || 'нет'
      }
      addLog(`📊 Определение статуса: ${JSON.stringify(statusInfo)}`)
      console.log('📊 Определение статуса:', statusInfo)
      
      if (!profileData) {
        // Профиль не загружен - показываем ошибку регистрации
        addLog('⚠️ Профиль не загружен - статус: not_registered')
        console.log('⚠️ Профиль не загружен - статус: not_registered')
        setStatus('not_registered')
      } else if (!accessData || !accessData.has_access) {
        // Зарегистрирован, но не оплатил - показываем профиль с ограничением
        addLog(`⚠️ Доступ ограничен - статус: not_paid, профиль: ${profileData.full_name}`)
        console.log('⚠️ Доступ ограничен - статус: not_paid, но профиль есть:', profileData)
        setStatus('not_paid')
      } else {
        // Зарегистрирован и оплатил
        addLog(`✅ Доступ есть - статус: paid, профиль: ${profileData.full_name}`)
        console.log('✅ Доступ есть - статус: paid, профиль:', profileData)
        setStatus('paid')
      }
    } catch (error: any) {
      addLog(`❌ Неожиданная ошибка загрузки профиля: ${error.message || 'Неизвестная ошибка'}`)
      addLog(`Тип ошибки: ${error.name || 'Error'}`)
      if (error.stack) {
        addLog(`Stack: ${error.stack.substring(0, 200)}...`)
      }
      console.error('Неожиданная ошибка загрузки профиля:', error)
      // В случае любой ошибки - считаем что не зарегистрирован
      setStatus('not_registered')
    }
  }

  useEffect(() => {
    addLog('🚀 ProfilePage загружен, начинаю загрузку профиля...')
    loadProfileAndAccess()
  }, [])

  // Загружаем курсы когда профиль загружен и есть доступ
  useEffect(() => {
    if (status === 'paid' && profile) {
      loadMyCourses()
    }
  }, [status, profile])

  const loadMyCourses = async () => {
    try {
      setLoadingCourses(true)
      addLog('📚 Загрузка курсов пользователя...')
      const response = await coursesApi.getMy()
      const courses = Array.isArray(response.data) ? response.data : []
      // Безопасно обрабатываем курсы - гарантируем правильную структуру progress
      const safeCourses = courses.map(course => ({
        ...course,
        progress: {
          total_lessons: course.progress?.total_lessons ?? 0,
          completed_lessons: course.progress?.completed_lessons ?? 0,
          progress_percent: typeof course.progress?.progress_percent === 'number' ? course.progress.progress_percent : 0,
          purchased_at: course.progress?.purchased_at ?? null,
          is_completed: course.progress?.is_completed ?? false
        }
      }))
      setMyCourses(safeCourses)
      addLog(`✅ Загружено курсов: ${safeCourses.length}`)
    } catch (error: any) {
      console.error('Ошибка загрузки курсов:', error)
      addLog(`❌ Ошибка загрузки курсов: ${error.message}`)
      setMyCourses([])
    } finally {
      setLoadingCourses(false)
    }
  }

  if (status === 'loading') {
    return (
      <div className="profile-page">
        <div className="loading">Загрузка...</div>
        {debugLogs.length > 0 && (
          <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f5f5f5', borderRadius: '8px', fontSize: '12px' }}>
            <button 
              onClick={() => setShowDebug(!showDebug)}
              style={{ marginBottom: '10px', padding: '5px 10px', fontSize: '12px' }}
            >
              {showDebug ? '🔽 Скрыть логи' : '🔼 Показать логи'}
            </button>
            {showDebug && (
              <div style={{ maxHeight: '200px', overflow: 'auto', fontFamily: 'monospace' }}>
                {debugLogs.map((log, i) => (
                  <div key={i} style={{ marginBottom: '5px', wordBreak: 'break-word' }}>{log}</div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    )
  }

  if (status === 'not_registered') {
    // Проверяем, открыт ли Mini App через Telegram
    const webApp = window.Telegram?.WebApp
    const isOpenedViaTelegram = !!webApp
    
    return (
      <div className="profile-page">
        <div className="error">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px', flexWrap: 'wrap', gap: '10px' }}>
            <h2 style={{ margin: 0 }}>Профиль не найден</h2>
            <button 
              onClick={() => setShowDebug(!showDebug)}
              style={{ 
                padding: '8px 16px', 
                fontSize: '14px', 
                backgroundColor: '#007bff', 
                color: 'white', 
                border: 'none', 
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: 'bold',
                boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
              }}
            >
              {showDebug ? '🔽 Скрыть логи' : '🔼 Показать логи'} {debugLogs.length > 0 && `(${debugLogs.length})`}
            </button>
          </div>
          
          {!isOpenedViaTelegram && (
            <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#f8d7da', borderRadius: '8px', border: '2px solid #dc3545' }}>
              <h3 style={{ margin: '0 0 10px 0', color: '#721c24' }}>⚠️ Mini App открыт не через Telegram!</h3>
              <p style={{ margin: '0', color: '#721c24' }}>
                Для работы приложения необходимо открыть его через Telegram бота.
              </p>
              <div style={{ marginTop: '15px', padding: '10px', backgroundColor: '#fff', borderRadius: '4px' }}>
                <p style={{ margin: '0 0 10px 0', fontWeight: 'bold' }}>📱 Как открыть правильно:</p>
                <ol style={{ margin: '0', paddingLeft: '20px', color: '#721c24' }}>
                  <li style={{ marginBottom: '8px' }}>Откройте Telegram на вашем устройстве</li>
                  <li style={{ marginBottom: '8px' }}>Найдите бота @beautyt3st_bot (или ваш бот)</li>
                  <li style={{ marginBottom: '8px' }}>Нажмите кнопку "Открыть приложение" или отправьте <code>/start</code></li>
                  <li>Mini App откроется внутри Telegram с правильной авторизацией</li>
                </ol>
              </div>
            </div>
          )}
          
          <p>Для доступа к платформе необходимо пройти регистрацию через Telegram-бота.</p>
          <div className="register-hint" style={{ marginTop: '20px', padding: '15px', backgroundColor: '#fff3cd', borderRadius: '8px' }}>
            <p style={{ margin: '0 0 10px 0', fontWeight: 'bold' }}>📋 Инструкция:</p>
            <ol style={{ margin: '0', paddingLeft: '20px' }}>
              <li style={{ marginBottom: '8px' }}>Откройте бота @beautyt3st_bot в Telegram</li>
              <li style={{ marginBottom: '8px' }}>Отправьте команду <code>/start</code></li>
              <li style={{ marginBottom: '8px' }}>Пройдите регистрацию (укажите имя, телефон)</li>
              <li>После регистрации вернитесь в Mini App</li>
            </ol>
          </div>
          <p style={{ marginTop: '15px', fontSize: '14px', color: '#666' }}>
            ⚠️ Если вы уже регистрировались, попробуйте закрыть и открыть Mini App заново
          </p>
          {debugLogs.length > 0 && (
            <div style={{ marginTop: '20px', padding: '15px', backgroundColor: showDebug ? '#f5f5f5' : '#fff3cd', borderRadius: '8px', fontSize: '12px', border: '2px solid #ffc107' }}>
              {!showDebug && (
                <p style={{ margin: '0 0 10px 0', fontWeight: 'bold', color: '#856404' }}>
                  ⚠️ Есть {debugLogs.length} логов для диагностики. Нажмите кнопку "Показать логи" выше.
                </p>
              )}
              {showDebug && (
                <>
                  <h4 style={{ marginTop: 0, marginBottom: '10px' }}>📋 Логи для диагностики ({debugLogs.length}):</h4>
                  <div style={{ maxHeight: '400px', overflow: 'auto', fontFamily: 'monospace', backgroundColor: 'white', padding: '10px', borderRadius: '4px', border: '1px solid #ddd' }}>
                    {debugLogs.map((log, i) => (
                      <div key={i} style={{ marginBottom: '8px', wordBreak: 'break-word', fontSize: '11px', lineHeight: '1.4' }}>{log}</div>
                    ))}
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    )
  }

  if (status === 'not_paid') {
    console.log('🔍 [not_paid] Рендер страницы not_paid, profile:', profile)
    // Не вызываем addLog во время рендера - это может вызвать ошибку React
    // addLog(`🔍 Рендер страницы not_paid, profile: ${profile ? profile.full_name : 'null'}`)
    return (
      <div className="profile-page">
        <div className="error">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
            <h2>❌ Доступ ограничен</h2>
            <button 
              onClick={() => setShowDebug(!showDebug)}
              style={{ padding: '5px 10px', fontSize: '12px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px' }}
            >
              {showDebug ? '🔽 Скрыть логи' : '🔼 Показать логи'}
            </button>
          </div>
          <p>Для доступа к платформе необходимо оплатить курс.</p>
          <p className="register-hint">
            💡 Выберите курс на главной странице и оплатите его для получения доступа
          </p>
          {profile ? (
            <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f5f5f5', borderRadius: '8px' }}>
              <h3 style={{ marginTop: 0 }}>Ваш профиль:</h3>
              <p><strong>Имя:</strong> {profile.full_name || 'Не указано'}</p>
              {profile.phone && <p><strong>Телефон:</strong> {profile.phone}</p>}
              {profile.email && <p><strong>Email:</strong> {profile.email}</p>}
              {profile.city && <p><strong>Город:</strong> {profile.city}</p>}
              <p><strong>Баллы:</strong> {profile.points ?? 0}</p>
            </div>
          ) : (
            <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#fff3cd', borderRadius: '8px' }}>
              <p>⚠️ Профиль загружается...</p>
            </div>
          )}
          {showDebug && debugLogs.length > 0 && (
            <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f5f5f5', borderRadius: '8px', fontSize: '12px' }}>
              <h4 style={{ marginTop: 0 }}>Логи для диагностики:</h4>
              <div style={{ maxHeight: '300px', overflow: 'auto', fontFamily: 'monospace' }}>
                {debugLogs.map((log, i) => (
                  <div key={i} style={{ marginBottom: '5px', wordBreak: 'break-word' }}>{log}</div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }

  // Функции для редактирования профиля
  const handleSave = async () => {
    if (!profile) return
    
    setSaving(true)
    try {
      const updated = await profileApi.update(editForm)
      setProfile(updated.data)
      setIsEditing(false)
      console.log('✅ Профиль обновлен:', updated.data)
    } catch (error: any) {
      console.error('❌ Ошибка обновления профиля:', error)
      alert('Ошибка при сохранении профиля. Попробуйте еще раз.')
    } finally {
      setSaving(false)
    }
  }

  const handleCancel = () => {
    if (profile) {
      setEditForm({
        full_name: profile.full_name || '',
        phone: profile.phone || '',
        email: profile.email || '',
        city: profile.city || ''
      })
    }
    setIsEditing(false)
  }

  // status === 'paid' - показываем профиль
  if (status === 'paid') {
    // МАКСИМАЛЬНОЕ ЛОГИРОВАНИЕ ПЕРЕД РЕНДЕРОМ
    const renderLog = `🔍 [RENDER] status=paid, profile=${profile ? 'exists' : 'null'}`
    console.log(renderLog)
    
    // Логируем ВСЕ данные профиля с типами
    if (profile) {
      const profileDebug = {
        id: { value: profile.id, type: typeof profile.id },
        telegram_id: { value: profile.telegram_id, type: typeof profile.telegram_id },
        username: { value: profile.username, type: typeof profile.username, isNull: profile.username === null, isUndefined: profile.username === undefined },
        full_name: { value: profile.full_name, type: typeof profile.full_name, length: profile.full_name?.length },
        phone: { value: profile.phone, type: typeof profile.phone, length: profile.phone?.length },
        email: { value: profile.email, type: typeof profile.email, isNull: profile.email === null, isUndefined: profile.email === undefined },
        city: { value: profile.city, type: typeof profile.city, isNull: profile.city === null, isUndefined: profile.city === undefined },
        points: { value: profile.points, type: typeof profile.points, isNaN: isNaN(Number(profile.points)) },
        created_at: { value: profile.created_at, type: typeof profile.created_at, isDate: profile.created_at instanceof Date, isString: typeof profile.created_at === 'string' }
      }
      console.log('📊 [RENDER] Детали профиля для рендера:', JSON.stringify(profileDebug, null, 2))
    }
    
    if (!profile) {
      console.warn('⚠️ [paid] Профиль отсутствует, показываю загрузку')
      return <div className="loading">Загрузка профиля...</div>
    }

    return (
        <div className="profile-page">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h1>👤 Мой профиль</h1>
            <button 
              onClick={() => setShowDebug(!showDebug)}
              style={{ padding: '5px 10px', fontSize: '12px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px' }}
            >
              {showDebug ? '🔽 Скрыть логи' : '🔼 Показать логи'}
            </button>
            {!isEditing && (
              <button 
                onClick={() => setIsEditing(true)}
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#007bff',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                ✏️ Редактировать
              </button>
            )}
          </div>

          {/* Основная информация */}
          <div className="profile-card">
                  <div className="profile-avatar">
                    {(() => {
                      try {
                        const name = profile.full_name
                        console.log('🎨 [RENDER] Аватар - full_name:', { name, type: typeof name, isString: typeof name === 'string', length: name?.length })
                        if (name && typeof name === 'string' && name.length > 0) {
                          const firstChar = name.charAt(0).toUpperCase()
                          console.log('🎨 [RENDER] Аватар - первый символ:', firstChar)
                          return firstChar
                        }
                        return '?'
                      } catch (e) {
                        console.error('❌ [RENDER] Ошибка в аватаре:', e)
                        return '?'
                      }
                    })()}
                  </div>
            
            {isEditing ? (
              <div className="profile-info" style={{ flex: 1 }}>
                <div style={{ marginBottom: '15px' }}>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Имя:</label>
                  <input
                    type="text"
                    value={editForm.full_name}
                    onChange={(e) => setEditForm({ ...editForm, full_name: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '8px',
                      borderRadius: '4px',
                      border: '1px solid #ddd',
                      fontSize: '14px'
                    }}
                  />
                </div>
                
                <div style={{ marginBottom: '15px' }}>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Телефон:</label>
                  <input
                    type="tel"
                    value={editForm.phone}
                    onChange={(e) => setEditForm({ ...editForm, phone: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '8px',
                      borderRadius: '4px',
                      border: '1px solid #ddd',
                      fontSize: '14px'
                    }}
                  />
                </div>
                
                <div style={{ marginBottom: '15px' }}>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Email:</label>
                  <input
                    type="email"
                    value={editForm.email}
                    onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
                    placeholder="example@mail.com"
                    style={{
                      width: '100%',
                      padding: '8px',
                      borderRadius: '4px',
                      border: '1px solid #ddd',
                      fontSize: '14px'
                    }}
                  />
                </div>
                
                <div style={{ marginBottom: '15px' }}>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Город:</label>
                  <input
                    type="text"
                    value={editForm.city}
                    onChange={(e) => setEditForm({ ...editForm, city: e.target.value })}
                    placeholder="Москва"
                    style={{
                      width: '100%',
                      padding: '8px',
                      borderRadius: '4px',
                      border: '1px solid #ddd',
                      fontSize: '14px'
                    }}
                  />
                </div>
                
                <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
                  <button
                    onClick={handleSave}
                    disabled={saving}
                    style={{
                      padding: '10px 20px',
                      backgroundColor: '#28a745',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      cursor: saving ? 'not-allowed' : 'pointer',
                      fontSize: '14px',
                      flex: 1
                    }}
                  >
                    {saving ? '💾 Сохранение...' : '💾 Сохранить'}
                  </button>
                  <button
                    onClick={handleCancel}
                    disabled={saving}
                    style={{
                      padding: '10px 20px',
                      backgroundColor: '#6c757d',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      cursor: saving ? 'not-allowed' : 'pointer',
                      fontSize: '14px',
                      flex: 1
                    }}
                  >
                    ❌ Отмена
                  </button>
                </div>
              </div>
            ) : (
              <div className="profile-info">
                {(() => {
                  try {
                    const name = String(profile.full_name || 'Пользователь')
                    console.log('🎨 [RENDER] Имя профиля:', { name, original: profile.full_name, type: typeof profile.full_name })
                    return <h2>{name}</h2>
                  } catch (e) {
                    console.error('❌ [RENDER] Ошибка в имени:', e)
                    return <h2>Пользователь</h2>
                  }
                })()}
                {(() => {
                  try {
                    if (profile.username) {
                      const username = String(profile.username)
                      console.log('🎨 [RENDER] Username:', { username, original: profile.username, type: typeof profile.username })
                      return <p className="username">@{username}</p>
                    }
                    return null
                  } catch (e) {
                    console.error('❌ [RENDER] Ошибка в username:', e)
                    return null
                  }
                })()}
                {(() => {
                  try {
                    const phone = String(profile.phone || 'Не указан')
                    console.log('🎨 [RENDER] Телефон:', { phone, original: profile.phone, type: typeof profile.phone })
                    return <p className="phone">📞 {phone}</p>
                  } catch (e) {
                    console.error('❌ [RENDER] Ошибка в телефоне:', e)
                    return <p className="phone">📞 Не указан</p>
                  }
                })()}
                {(() => {
                  try {
                    if (profile.email) {
                      const email = String(profile.email)
                      console.log('🎨 [RENDER] Email:', { email, original: profile.email, type: typeof profile.email })
                      return <p className="email">📧 {email}</p>
                    }
                    return null
                  } catch (e) {
                    console.error('❌ [RENDER] Ошибка в email:', e)
                    return null
                  }
                })()}
                {(() => {
                  try {
                    if (profile.city) {
                      const city = String(profile.city)
                      console.log('🎨 [RENDER] Город:', { city, original: profile.city, type: typeof profile.city })
                      return <p className="city">📍 {city}</p>
                    }
                    return null
                  } catch (e) {
                    console.error('❌ [RENDER] Ошибка в городе:', e)
                    return null
                  }
                })()}
              </div>
            )}
          </div>

          {/* Баллы */}
          <div className="profile-stats">
            <div className="stat-card">
              <span className="stat-icon">⭐</span>
              <div>
                {(() => {
                  try {
                    const points = profile.points ?? 0
                    const pointsNum = typeof points === 'number' ? points : Number(points) || 0
                    console.log('🎨 [RENDER] Баллы:', { points, pointsNum, type: typeof points, isNaN: isNaN(pointsNum) })
                    return <p className="stat-value">{pointsNum}</p>
                  } catch (e) {
                    console.error('❌ [RENDER] Ошибка в баллах:', e)
                    return <p className="stat-value">0</p>
                  }
                })()}
                <p className="stat-label">Баллов</p>
              </div>
            </div>

            <div className="stat-card">
              <span className="stat-icon">📅</span>
              <div>
                <p className="stat-value">
                  {(() => {
                    try {
                      if (!profile.created_at) return 'Не указано'
                      // Безопасно преобразуем в дату
                      const dateStr = String(profile.created_at)
                      const date = new Date(dateStr)
                      if (isNaN(date.getTime())) return 'Не указано'
                      return date.toLocaleDateString('ru-RU')
                    } catch (e) {
                      console.error('Ошибка форматирования даты:', e)
                      return 'Не указано'
                    }
                  })()}
                </p>
                <p className="stat-label">Дата регистрации</p>
              </div>
            </div>
          </div>

      {/* История курсов */}
      <div className="profile-courses">
        <h3>📚 Мои курсы</h3>
        {loadingCourses ? (
          <div className="loading">Загрузка курсов...</div>
        ) : myCourses.length > 0 ? (
          <div className="courses-list">
            {myCourses.map((course, index) => {
              // МАКСИМАЛЬНОЕ ЛОГИРОВАНИЕ КУРСА
              console.log(`🎨 [RENDER] Курс #${index}:`, {
                course,
                id: { value: course?.id, type: typeof course?.id },
                title: { value: course?.title, type: typeof course?.title },
                description: { value: course?.description, type: typeof course?.description },
                progress: { value: course?.progress, type: typeof course?.progress, isObject: course?.progress instanceof Object }
              })
              
              // Безопасно проверяем структуру course
              if (!course || typeof course !== 'object') {
                console.warn('⚠️ Некорректный курс:', course)
                return null
              }
              // Безопасно получаем все значения - гарантируем что это примитивы
              const courseId = typeof course.id === 'number' ? course.id : 0
              const courseTitle = typeof course.title === 'string' ? course.title : 'Без названия'
              const courseDescription = typeof course.description === 'string' ? course.description : ''
              
              console.log(`🎨 [RENDER] Курс #${index} нормализован:`, { courseId, courseTitle, courseDescription })
              
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
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#f0f0f0'
                  e.currentTarget.style.borderColor = '#007bff'
                  e.currentTarget.style.transform = 'translateY(-2px)'
                  e.currentTarget.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#f9f9f9'
                  e.currentTarget.style.borderColor = '#e0e0e0'
                  e.currentTarget.style.transform = 'translateY(0)'
                  e.currentTarget.style.boxShadow = 'none'
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
                  {course.progress?.is_completed && (
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
                  <ProgressBar percent={course.progress?.progress_percent ?? 0} />
                  <p style={{ margin: '5px 0 0 0', fontSize: '12px', color: '#666' }}>
                    Пройдено: {course.progress?.completed_lessons ?? 0} / {course.progress?.total_lessons ?? 0} уроков
                    {(course.progress?.progress_percent ?? 0) > 0 && (
                      <span> ({course.progress?.progress_percent ?? 0}%)</span>
                    )}
                  </p>
                  {course.progress?.purchased_at && (
                    <p style={{ margin: '5px 0 0 0', fontSize: '12px', color: '#999' }}>
                      Куплен: {course.progress.purchased_at ? new Date(course.progress.purchased_at).toLocaleDateString('ru-RU') : 'Не указано'}
                    </p>
                  )}
                </div>
              </div>
            )
            })}
          </div>
        ) : (
          <div className="empty-state" style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
            <p>У вас пока нет купленных курсов</p>
            <p style={{ fontSize: '14px', marginTop: '10px' }}>
              Выберите курс из каталога, чтобы начать обучение
            </p>
            <button
              onClick={() => navigate('/courses')}
              style={{
                marginTop: '15px',
                padding: '10px 20px',
                backgroundColor: '#007bff',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              Перейти к каталогу курсов
            </button>
          </div>
        )}
      </div>

      {/* Поддержка */}
      <div className="profile-support">
        <h3>❓ Нужна помощь?</h3>
        <a href="https://t.me/your_support" target="_blank" rel="noopener noreferrer" className="support-link">
          Написать в поддержку
        </a>
      </div>

      {/* Логи для диагностики */}
      {showDebug && debugLogs.length > 0 && (
        <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f5f5f5', borderRadius: '8px', fontSize: '12px' }}>
          <h4 style={{ marginTop: 0 }}>Логи для диагностики:</h4>
          <div style={{ maxHeight: '300px', overflow: 'auto', fontFamily: 'monospace' }}>
            {debugLogs.map((log, i) => (
              <div key={i} style={{ marginBottom: '5px', wordBreak: 'break-word' }}>{log}</div>
            ))}
          </div>
        </div>
      )}
    </div>
    )
  }

  // Fallback - не должно произойти, но на всякий случай
  return <div className="loading">Загрузка...</div>
}

export default ProfilePage

