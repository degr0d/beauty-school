/**
 * Компонент для выбора telegram_id в режиме разработки
 * Показывается только на localhost
 */

import { useState, useEffect } from 'react'
import { profileApi, DevUser } from '../api/client'

const DevModeSelector = () => {
  // Проверяем видимость сразу при инициализации
  const hostname = window.location.hostname
  const isLocalhost = hostname === 'localhost' || 
                     hostname === '127.0.0.1' ||
                     hostname.includes('localhost') ||
                     hostname === ''
  
  const urlParams = new URLSearchParams(window.location.search)
  const hasDevParam = urlParams.get('dev') === 'true'
  
  // На localhost ВСЕГДА показываем, даже если есть Telegram WebApp
  // Проверяем, есть ли реальный initData
  const webApp = window.Telegram?.WebApp
  const hasRealInitData = webApp?.initData && webApp.initData.trim().length > 0
  const notInTelegram = !hasRealInitData
  
  const shouldShow = isLocalhost || hasDevParam || notInTelegram
  
  const [isVisible] = useState(shouldShow)
  const [telegramId, setTelegramId] = useState<string>(() => {
    const savedId = localStorage.getItem('dev_telegram_id')
    return savedId || '123456789'
  })
  const [isOpen, setIsOpen] = useState(false)
  const [users, setUsers] = useState<DevUser[]>([])
  const [loadingUsers, setLoadingUsers] = useState(false)

  useEffect(() => {
    console.log('🔧 [DevModeSelector] Компонент смонтирован:', {
      hostname,
      isLocalhost,
      hasDevParam,
      notInTelegram,
      shouldShow,
      isVisible,
      hasTelegram: !!window.Telegram?.WebApp
    })
  }, [])

  useEffect(() => {
    // Загружаем список пользователей при открытии панели
    if (isOpen && isVisible) {
      loadUsers()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen])

  const loadUsers = async () => {
    setLoadingUsers(true)
    try {
      const response = await profileApi.getDevUsers()
      setUsers(response.data.users || [])
    } catch (error) {
      console.error('Ошибка загрузки пользователей:', error)
      setUsers([])
    } finally {
      setLoadingUsers(false)
    }
  }

  const handleSave = () => {
    if (telegramId && !isNaN(Number(telegramId))) {
      localStorage.setItem('dev_telegram_id', telegramId)
      alert(`✅ Telegram ID установлен: ${telegramId}\n\nПерезагрузите страницу для применения изменений.`)
      window.location.reload()
    } else {
      alert('❌ Введите корректный Telegram ID (число)')
    }
  }

  // Всегда показываем в режиме разработки, но логируем для отладки
  if (!isVisible) {
    console.log('🔧 [DevModeSelector] Компонент скрыт, isVisible=false')
    return null
  }

  console.log('🔧 [DevModeSelector] Компонент отображается')

  return (
    <div style={{
      position: 'fixed',
      top: '10px',
      right: '10px',
      zIndex: 10000,
      backgroundColor: '#fff3cd',
      border: '2px solid #ffc107',
      borderRadius: '8px',
      padding: '12px',
      boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
      maxWidth: '300px',
      fontFamily: 'system-ui, sans-serif',
      fontSize: '14px'
    }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '8px'
      }}>
        <strong style={{ color: '#856404' }}>🔧 Режим разработки</strong>
        <button
          onClick={() => setIsOpen(!isOpen)}
          style={{
            background: 'none',
            border: 'none',
            fontSize: '18px',
            cursor: 'pointer',
            color: '#856404'
          }}
        >
          {isOpen ? '−' : '+'}
        </button>
      </div>
      
      {isOpen && (
        <div>
          <p style={{ margin: '0 0 8px 0', color: '#856404', fontSize: '12px' }}>
            Укажите ваш Telegram ID для локальной разработки:
          </p>
          
          {/* Список пользователей из БД */}
          {users.length > 0 && (
            <div style={{ marginBottom: '8px' }}>
              <p style={{ margin: '0 0 4px 0', color: '#856404', fontSize: '11px', fontWeight: 'bold' }}>
                👥 Пользователи из БД:
              </p>
              <select
                value={telegramId}
                onChange={(e) => setTelegramId(e.target.value)}
                style={{
                  width: '100%',
                  padding: '6px',
                  border: '1px solid #ffc107',
                  borderRadius: '4px',
                  fontSize: '12px',
                  marginBottom: '4px',
                  backgroundColor: '#fff'
                }}
              >
                <option value="">-- Выберите пользователя --</option>
                {users.map((user) => (
                  <option key={user.id} value={user.telegram_id}>
                    {user.full_name} (ID: {user.telegram_id})
                  </option>
                ))}
              </select>
            </div>
          )}
          
          {loadingUsers && (
            <p style={{ margin: '4px 0', color: '#856404', fontSize: '11px' }}>
              Загрузка пользователей...
            </p>
          )}
          
          <input
            type="text"
            value={telegramId}
            onChange={(e) => setTelegramId(e.target.value)}
            placeholder="123456789"
            style={{
              width: '100%',
              padding: '6px',
              border: '1px solid #ffc107',
              borderRadius: '4px',
              marginBottom: '8px',
              fontSize: '14px'
            }}
          />
          <button
            onClick={handleSave}
            style={{
              width: '100%',
              padding: '8px',
              backgroundColor: '#ffc107',
              color: '#000',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: 'bold',
              fontSize: '14px'
            }}
          >
            💾 Сохранить и перезагрузить
          </button>
          <p style={{ 
            margin: '8px 0 0 0', 
            color: '#856404', 
            fontSize: '11px',
            fontStyle: 'italic'
          }}>
            Текущий ID: {localStorage.getItem('dev_telegram_id') || '123456789'}
          </p>
          <p style={{ 
            margin: '8px 0 0 0', 
            color: '#856404', 
            fontSize: '11px'
          }}>
            💡 Выберите пользователя из списка или введите Telegram ID вручную
          </p>
        </div>
      )}
    </div>
  )
}

export default DevModeSelector

