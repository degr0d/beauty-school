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
          message: error.message
        })
        
        // Если 404 - пользователь не зарегистрирован
        if (error.response?.status === 404) {
          console.log('⚠️ Пользователь не найден (404)')
          setStatus('not_registered')
          return
        }
        
        // Если 401 - проблема с авторизацией
        if (error.response?.status === 401) {
          console.log('⚠️ Проблема с авторизацией (401)')
          console.log('💡 Проверьте что открываете Mini App через бота в Telegram')
          setStatus('not_registered')
          return
        }
        
        // Другая ошибка - тоже считаем не зарегистрирован
        setStatus('not_registered')
        return
      }

      // Если профиль загружен - проверяем доступ
      let accessData: AccessStatus | null = null
      
      try {
        const accessResponse = await accessApi.checkAccess()
        accessData = accessResponse.data
      } catch (error: any) {
        // Если 404 - пользователь не зарегистрирован
        if (error.response?.status === 404) {
          setStatus('not_registered')
          return
        }
        // Другая ошибка - считаем что нет доступа
        console.error('Ошибка проверки доступа:', error)
        accessData = { has_access: false, purchased_courses_count: 0, total_payments: 0 }
      }

      // Сохраняем данные
      setProfile(profileData)
      setAccessStatus(accessData)

      // Определяем статус
      if (!accessData || !accessData.has_access) {
        // Зарегистрирован, но не оплатил
        setStatus('not_paid')
      } else {
        // Зарегистрирован и оплатил
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

      return (
        <div className="profile-page">
          <h1>👤 Мой профиль</h1>

          {/* Основная информация */}
          <div className="profile-card">
            <div className="profile-avatar">
              {profile.full_name.charAt(0).toUpperCase()}
            </div>
            
            <div className="profile-info">
              <h2>{profile.full_name}</h2>
              {profile.username && <p className="username">@{profile.username}</p>}
              <p className="phone">{profile.phone}</p>
              {profile.city && <p className="city">📍 {profile.city}</p>}
            </div>
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

