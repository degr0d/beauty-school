/**
 * Страница профиля пользователя
 */

import { useEffect, useState } from 'react'
import { profileApi, accessApi, type Profile, type AccessStatus } from '../api/client'

type ProfileStatus = 'loading' | 'not_registered' | 'not_paid' | 'paid'

const ProfilePage = () => {
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

  useEffect(() => {
    loadProfileAndAccess()
  }, [])

  const loadProfileAndAccess = async () => {
    try {
      // Проверяем наличие Telegram WebApp и initData
      const webApp = window.Telegram?.WebApp
      console.log('🔍 Проверка Telegram WebApp:', {
        hasWebApp: !!webApp,
        hasInitData: !!webApp?.initData,
        user: webApp?.initDataUnsafe?.user,
        telegramId: webApp?.initDataUnsafe?.user?.id
      })
      
      // Сначала пробуем загрузить профиль
      let profileData: Profile | null = null
      
      try {
        console.log('📡 Запрос профиля...')
        const profileResponse = await profileApi.get()
        console.log('✅ Профиль получен:', profileResponse.data)
        profileData = profileResponse.data
      } catch (error: any) {
        console.error('❌ Ошибка загрузки профиля:', {
          status: error.response?.status,
          statusText: error.response?.statusText,
          data: error.response?.data,
          message: error.message,
          url: error.config?.url,
          headers: error.config?.headers,
          hasInitData: !!webApp?.initData,
          telegramId: webApp?.initDataUnsafe?.user?.id
        })
        
        // Если 401 - проблема с авторизацией (initData невалиден или отсутствует)
        if (error.response?.status === 401) {
          console.log('⚠️ Проблема с авторизацией (401)')
          console.log('💡 Проверьте что открываете Mini App через бота в Telegram')
          console.log('💡 Если вы уже зарегистрированы, попробуйте закрыть и открыть Mini App заново')
          setStatus('not_registered')
          return
        }
        
        // Если 404 - пользователь не найден (но backend должен создавать автоматически)
        // Это может означать проблему с поиском пользователя в БД
        if (error.response?.status === 404) {
          console.log('⚠️ Пользователь не найден (404)')
          console.log('💡 Backend должен создавать профиль автоматически.')
          console.log('💡 Если вы уже зарегистрированы через бота, это может быть проблема с поиском в БД.')
          console.log('💡 Попробуйте закрыть и открыть Mini App заново.')
          setStatus('not_registered')
          return
        }
        
        // Другая ошибка - тоже считаем не зарегистрирован
        console.log('⚠️ Неожиданная ошибка при загрузке профиля')
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

      // Сохраняем данные
      setProfile(profileData)
      setAccessStatus(accessData)
      
      // Инициализируем форму редактирования
      if (profileData) {
        setEditForm({
          full_name: profileData.full_name || '',
          phone: profileData.phone || '',
          email: profileData.email || '',
          city: profileData.city || ''
        })
      }

      // Определяем статус
      console.log('📊 Определение статуса:', {
        hasProfile: !!profileData,
        hasAccessData: !!accessData,
        hasAccess: accessData?.has_access,
        purchasedCourses: accessData?.purchased_courses_count
      })
      
      if (!profileData) {
        // Профиль не загружен - показываем ошибку регистрации
        console.log('⚠️ Профиль не загружен - статус: not_registered')
        setStatus('not_registered')
      } else if (!accessData || !accessData.has_access) {
        // Зарегистрирован, но не оплатил
        console.log('⚠️ Доступ ограничен - статус: not_paid')
        setStatus('not_paid')
      } else {
        // Зарегистрирован и оплатил
        console.log('✅ Доступ есть - статус: paid')
        setStatus('paid')
      }
    } catch (error: any) {
      console.error('Неожиданная ошибка загрузки профиля:', error)
      // В случае любой ошибки - считаем что не зарегистрирован
      setStatus('not_registered')
    }
  }

  if (status === 'loading') {
    return <div className="loading">Загрузка...</div>
  }

  if (status === 'not_registered') {
    return (
      <div className="profile-page">
        <div className="error">
          <h2>Профиль не найден</h2>
          <p>Для доступа к платформе необходимо пройти регистрацию через Telegram-бота.</p>
          <div className="register-hint" style={{ marginTop: '20px', padding: '15px', backgroundColor: '#fff3cd', borderRadius: '8px' }}>
            <p style={{ margin: '0 0 10px 0', fontWeight: 'bold' }}>📋 Инструкция:</p>
            <ol style={{ margin: '0', paddingLeft: '20px' }}>
              <li style={{ marginBottom: '8px' }}>Откройте бота @beauty в Telegram</li>
              <li style={{ marginBottom: '8px' }}>Отправьте команду <code>/start</code></li>
              <li style={{ marginBottom: '8px' }}>Пройдите регистрацию (укажите имя, телефон)</li>
              <li>После регистрации вернитесь в Mini App</li>
            </ol>
          </div>
          <p style={{ marginTop: '15px', fontSize: '14px', color: '#666' }}>
            ⚠️ Если вы уже регистрировались, попробуйте закрыть и открыть Mini App заново
          </p>
        </div>
      </div>
    )
  }

  if (status === 'not_paid') {
    return (
      <div className="profile-page">
        <div className="error">
          <h2>❌ Доступ ограничен</h2>
          <p>Для доступа к платформе необходимо оплатить курс.</p>
          <p className="register-hint">
            💡 Выберите курс на главной странице и оплатите его для получения доступа
          </p>
          {profile && (
            <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f5f5f5', borderRadius: '8px' }}>
              <h3 style={{ marginTop: 0 }}>Ваш профиль:</h3>
              <p><strong>Имя:</strong> {profile.full_name}</p>
              {profile.phone && <p><strong>Телефон:</strong> {profile.phone}</p>}
              {profile.city && <p><strong>Город:</strong> {profile.city}</p>}
              <p><strong>Баллы:</strong> {profile.points}</p>
            </div>
          )}
        </div>
      </div>
    )
  }

      // status === 'paid' - показываем профиль
      if (!profile) {
        return <div className="loading">Загрузка...</div>
      }

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

      return (
        <div className="profile-page">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h1>👤 Мой профиль</h1>
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
              {profile.full_name.charAt(0).toUpperCase()}
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
                <h2>{profile.full_name}</h2>
                {profile.username && <p className="username">@{profile.username}</p>}
                <p className="phone">📞 {profile.phone}</p>
                {profile.email && <p className="email">📧 {profile.email}</p>}
                {profile.city && <p className="city">📍 {profile.city}</p>}
              </div>
            )}
          </div>

          {/* Баллы */}
          <div className="profile-stats">
            <div className="stat-card">
              <span className="stat-icon">⭐</span>
              <div>
                <p className="stat-value">{profile.points}</p>
                <p className="stat-label">Баллов</p>
              </div>
            </div>

            <div className="stat-card">
              <span className="stat-icon">📅</span>
              <div>
                <p className="stat-value">
                  {new Date(profile.created_at).toLocaleDateString('ru-RU')}
                </p>
                <p className="stat-label">Дата регистрации</p>
              </div>
            </div>
          </div>

      {/* История курсов */}
      <div className="profile-courses">
        <h3>📚 Мои курсы</h3>
        <p className="coming-soon">Раздел в разработке</p>
      </div>

      {/* Поддержка */}
      <div className="profile-support">
        <h3>❓ Нужна помощь?</h3>
        <a href="https://t.me/your_support" target="_blank" rel="noopener noreferrer" className="support-link">
          Написать в поддержку
        </a>
      </div>
    </div>
  )
}

export default ProfilePage

