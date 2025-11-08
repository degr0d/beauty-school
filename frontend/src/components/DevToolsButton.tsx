/**
 * Кнопка для открытия DevTools в режиме разработки
 * В Telegram WebApp F12 не работает, поэтому добавляем альтернативные способы
 */

import { useState, useEffect } from 'react'

const DevToolsButton = () => {
  const [isVisible, setIsVisible] = useState(false)
  const [isDevMode, setIsDevMode] = useState(false)

  useEffect(() => {
    // Проверяем, находимся ли мы в режиме разработки
    const checkDevMode = () => {
      // Показываем кнопку если:
      // 1. Не в Telegram (localhost или dev режим)
      // 2. Или если есть параметр ?dev=true в URL
      const isLocalhost = window.location.hostname === 'localhost' || 
                         window.location.hostname === '127.0.0.1' ||
                         window.location.hostname.includes('localhost')
      const urlParams = new URLSearchParams(window.location.search)
      const hasDevParam = urlParams.get('dev') === 'true'
      const notInTelegram = !window.Telegram?.WebApp
      
      return isLocalhost || hasDevParam || notInTelegram
    }

    setIsDevMode(checkDevMode())
    setIsVisible(checkDevMode())

    // Обработчик клавиатуры для открытия DevTools
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl+Shift+I или Ctrl+Shift+J для открытия DevTools
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === 'I' || e.key === 'J')) {
        e.preventDefault()
        openDevTools()
      }
      // Alt+D для открытия DevTools
      if (e.altKey && e.key === 'd') {
        e.preventDefault()
        openDevTools()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  const openDevTools = () => {
    // Пытаемся открыть DevTools разными способами
    console.log('🔧 Попытка открыть DevTools...')
    
    // Способ 1: Прямой вызов (работает в некоторых браузерах)
    try {
      // @ts-ignore
      if (window.chrome && window.chrome.runtime) {
        console.log('💡 Используйте: Ctrl+Shift+I (Windows/Linux) или Cmd+Option+I (Mac)')
      }
    } catch (e) {
      console.warn('Не удалось открыть DevTools автоматически')
    }

    // Способ 2: Показываем инструкции
    alert(
      '🔧 Как открыть DevTools:\n\n' +
      '1. В браузере (не в Telegram):\n' +
      '   - Windows/Linux: Ctrl+Shift+I или F12\n' +
      '   - Mac: Cmd+Option+I\n\n' +
      '2. В Telegram WebApp:\n' +
      '   - Откройте приложение в браузере напрямую\n' +
      '   - Или используйте: window.location.href в консоли\n\n' +
      '3. Для мобильных устройств:\n' +
      '   - Используйте удаленную отладку Chrome DevTools'
    )

    // Способ 3: Пытаемся открыть в новом окне (если не в Telegram)
    if (!window.Telegram?.WebApp) {
      const newWindow = window.open('', '_blank')
      if (newWindow) {
        newWindow.document.write(`
          <html>
            <head><title>DevTools Helper</title></head>
            <body style="padding: 20px; font-family: monospace;">
              <h2>🔧 DevTools Helper</h2>
              <p>Откройте DevTools в основном окне:</p>
              <ul>
                <li>Windows/Linux: <strong>Ctrl+Shift+I</strong> или <strong>F12</strong></li>
                <li>Mac: <strong>Cmd+Option+I</strong></li>
              </ul>
              <p>Или используйте консоль браузера для отладки.</p>
              <button onclick="window.close()" style="padding: 10px 20px; margin-top: 20px;">Закрыть</button>
            </body>
          </html>
        `)
      }
    }
  }

  if (!isVisible) return null

  return (
    <button
      onClick={openDevTools}
      style={{
        position: 'fixed',
        bottom: '80px', // Выше навигации
        right: '10px',
        zIndex: 9998,
        padding: '8px 12px',
        backgroundColor: '#007bff',
        color: 'white',
        border: 'none',
        borderRadius: '20px',
        cursor: 'pointer',
        fontSize: '12px',
        fontWeight: 'bold',
        boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
        opacity: 0.8,
        transition: 'opacity 0.2s',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.opacity = '1'
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.opacity = '0.8'
      }}
      title="Открыть DevTools (Alt+D или Ctrl+Shift+I)"
    >
      🔧 DevTools
    </button>
  )
}

export default DevToolsButton

