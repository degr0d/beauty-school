/**
 * Главный компонент приложения
 * Настройка роутинга и инициализация Telegram WebApp
 */

import { useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { useTelegram } from './hooks/useTelegram'

// Pages
import MainPage from './pages/MainPage'
import CoursesPage from './pages/CoursesPage'
import CoursePage from './pages/CoursePage'
import LessonPage from './pages/LessonPage'
import ProfilePage from './pages/ProfilePage'
import CommunitiesPage from './pages/CommunitiesPage'
import PaymentPage from './pages/PaymentPage'
import LeaderboardPage from './pages/LeaderboardPage'
import ChallengesPage from './pages/ChallengesPage'
import AnalyticsPage from './pages/AnalyticsPage'

// Components
import Navigation from './components/Navigation'
import DevToolsButton from './components/DevToolsButton'
import DevModeSelector from './components/DevModeSelector'
import Onboarding from './components/Onboarding'

function App() {
  console.log('🎯 [App] Компонент App рендерится')
  const { webApp } = useTelegram()
  const [showOnboarding, setShowOnboarding] = useState(false)

  useEffect(() => {
    // Проверяем, проходил ли пользователь онбординг
    const onboardingCompleted = localStorage.getItem('onboarding_completed')
    if (!onboardingCompleted) {
      // Небольшая задержка перед показом онбординга
      setTimeout(() => {
        setShowOnboarding(true)
      }, 1000)
    }
  }, [])

  useEffect(() => {
    console.log('🚀 [App] Инициализация приложения...')
    console.log('📍 [App] Текущий URL:', window.location.href)
    console.log('📍 [App] Telegram WebApp доступен:', !!window.Telegram?.WebApp)
    
    // Информация о DevTools
    if (!window.Telegram?.WebApp || window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
      console.log('🔧 [DevTools] Режим разработки активен')
      console.log('💡 [DevTools] Горячие клавиши:')
      console.log('   - Alt + D: Показать инструкции по DevTools')
      console.log('   - Ctrl+Shift+I (Win/Linux) или Cmd+Option+I (Mac): Открыть DevTools')
      console.log('   - F12: Открыть DevTools (если доступно)')
    } else {
      console.log('💡 [DevTools] В Telegram WebApp F12 не работает')
      console.log('   Добавьте ?dev=true к URL для показа кнопки DevTools')
    }
    
    // Инициализация Telegram WebApp
    if (webApp) {
      console.log('✅ Telegram WebApp найден, инициализирую...')
      try {
        webApp.ready()
        webApp.expand()
        
        // Применяем тему Telegram, но принудительно устанавливаем белый фон если он черный
        const bgColor = webApp.backgroundColor || '#ffffff'
        // Если цвет слишком темный - используем белый
        const isDark = bgColor && (bgColor.toLowerCase() === '#000000' || bgColor.toLowerCase() === '#000' || bgColor === 'black')
        document.body.style.backgroundColor = isDark ? '#ffffff' : bgColor
        // Также устанавливаем фон для root
        const root = document.getElementById('root')
        if (root) {
          root.style.backgroundColor = isDark ? '#ffffff' : bgColor
        }
        
        // Убрано логирование объекта user - может вызывать проблемы
        console.log('✅ Telegram WebApp инициализирован')
      } catch (error) {
        console.error('❌ Ошибка инициализации Telegram WebApp:', error)
      }
    } else {
      // Fallback для разработки (когда не в Telegram)
      console.log('⚠️ Telegram WebApp не найден через хук, проверяю напрямую...')
      
      // Проверяем еще раз напрямую - может быть webApp загружается медленно
      if (window.Telegram?.WebApp) {
        console.log('✅ Telegram WebApp найден напрямую, используем его')
        const directWebApp = window.Telegram.WebApp
        try {
          directWebApp.ready()
          directWebApp.expand()
          document.body.style.backgroundColor = directWebApp.backgroundColor || '#ffffff'
        } catch (error) {
          console.error('❌ Ошибка инициализации прямого WebApp:', error)
        }
      } else {
        console.log('⚠️ Telegram WebApp действительно не найден, работаем в режиме разработки')
        console.log('💡 Это нормально, если открываете в браузере напрямую')
        document.body.style.backgroundColor = '#ffffff'
      }
    }
  }, [webApp])

  // Error Handler для отлова глобальных ошибок
  useEffect(() => {
    const handleError = (event: ErrorEvent) => {
      console.error('❌ Глобальная ошибка в приложении:', event.error)
      console.error('📍 Файл:', event.filename, 'Строка:', event.lineno, 'Колонка:', event.colno)
      console.error('📍 Сообщение:', event.message)
      
      // Показываем сообщение об ошибке только если это критическая ошибка
      if (event.error && event.error.toString().includes('ChunkLoadError')) {
        console.warn('⚠️ Ошибка загрузки чанка - возможно проблема с кешем')
        const errorDiv = document.createElement('div')
        errorDiv.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; background: #ff9800; color: white; padding: 16px; z-index: 9999; text-align: center;'
        errorDiv.innerHTML = '⚠️ Ошибка загрузки. <a href="#" onclick="window.location.reload()" style="color: white; text-decoration: underline;">Перезагрузить</a>'
        document.body.appendChild(errorDiv)
      }
    }

    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      console.error('❌ Необработанное отклонение промиса:', event.reason)
      console.error('📍 Promise:', event.promise)
    }

    window.addEventListener('error', handleError)
    window.addEventListener('unhandledrejection', handleUnhandledRejection)
    
    return () => {
      window.removeEventListener('error', handleError)
      window.removeEventListener('unhandledrejection', handleUnhandledRejection)
    }
  }, [])

  // Добавляем глобальные горячие клавиши для DevTools
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Alt+D для открытия DevTools (работает даже в Telegram WebApp)
      if (e.altKey && e.key === 'd') {
        e.preventDefault()
        console.log('🔧 Горячая клавиша Alt+D нажата - откройте DevTools вручную')
        console.log('💡 В Telegram WebApp используйте:')
        console.log('   1. Откройте приложение в браузере напрямую')
        console.log('   2. Или используйте удаленную отладку')
        console.log('   3. Или добавьте ?dev=true к URL для показа кнопки DevTools')
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  console.log('🎯 [App] Рендер JSX')
  
  try {
    return (
      <BrowserRouter>
        <div className="app">
          {/* Онбординг для новых пользователей */}
          {showOnboarding && (
            <Onboarding onComplete={() => setShowOnboarding(false)} />
          )}
          
          {/* Навигация */}
          <Navigation />
          
          {/* Кнопка DevTools для режима разработки */}
          <DevToolsButton />
          
          {/* Селектор Telegram ID для режима разработки */}
          <DevModeSelector />
          
          {/* Контент */}
          <main className="content">
            <Routes>
              <Route path="/" element={<MainPage />} />
              <Route path="/courses" element={<CoursesPage />} />
              <Route path="/courses/:id" element={<CoursePage />} />
              <Route path="/lessons/:id" element={<LessonPage />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/communities" element={<CommunitiesPage />} />
              <Route path="/payment/success" element={<PaymentPage />} />
              <Route path="/leaderboard" element={<LeaderboardPage />} />
              <Route path="/challenges" element={<ChallengesPage />} />
              <Route path="/analytics" element={<AnalyticsPage />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    )
  } catch (error) {
    console.error('❌ [App] Ошибка при рендере:', error)
    return (
      <div style={{ padding: '20px', color: 'red' }}>
        <h1>Ошибка рендера</h1>
        <p>{error instanceof Error ? error.message : String(error)}</p>
      </div>
    )
  }
}

export default App

