/**
 * Точка входа React приложения
 */

import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import ErrorBoundary from './components/ErrorBoundary'
import './styles/global.css'

// Сначала проверяем, что все импорты загрузились
console.log('🚀 [main.tsx] Запуск приложения...')
console.log('📍 [main.tsx] Root элемент:', document.getElementById('root'))
console.log('📍 [main.tsx] React доступен:', typeof React !== 'undefined')
console.log('📍 [main.tsx] ReactDOM доступен:', typeof ReactDOM !== 'undefined')
console.log('📍 [main.tsx] App доступен:', typeof App !== 'undefined')

// Обновляем HTML сразу, чтобы видеть что происходит
const rootElement = document.getElementById('root')
if (rootElement) {
  rootElement.innerHTML = `
    <div style="padding: 20px; text-align: center; font-family: sans-serif;">
      <h2>🚀 Загрузка приложения...</h2>
      <p>Проверка модулей...</p>
    </div>
  `
}

// Небольшая задержка чтобы убедиться что все загрузилось
setTimeout(() => {
  try {
    console.log('✅ [main.tsx] Начинаю рендер React...')
    const root = ReactDOM.createRoot(rootElement!)
    console.log('✅ [main.tsx] ReactDOM root создан')
    
    root.render(
  <React.StrictMode>
        <ErrorBoundary>
    <App />
        </ErrorBoundary>
  </React.StrictMode>,
)
    
    console.log('✅ [main.tsx] Приложение отрендерено')
  } catch (error) {
    console.error('❌ [main.tsx] КРИТИЧЕСКАЯ ОШИБКА при запуске:', error)
    if (rootElement) {
      rootElement.innerHTML = `
        <div style="padding: 20px; color: red; font-family: sans-serif;">
          <h1>❌ Критическая ошибка загрузки</h1>
          <p><strong>Ошибка:</strong> ${error instanceof Error ? error.message : String(error)}</p>
          ${error instanceof Error && error.stack ? `<pre style="font-size: 12px; overflow: auto;">${error.stack}</pre>` : ''}
          <button onclick="window.location.reload()" style="margin-top: 20px; padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">Перезагрузить</button>
        </div>
      `
    }
  }
}, 100)

