/**
 * React Hook для работы с Telegram WebApp SDK
 */

import { useEffect, useState } from 'react'

// Типы для Telegram WebApp
interface TelegramWebApp {
  ready: () => void
  expand: () => void
  close: () => void
  initData: string
  initDataUnsafe: {
    user?: {
      id: number
      first_name: string
      last_name?: string
      username?: string
      language_code?: string
    }
    query_id?: string
    auth_date?: number
    hash?: string
  }
  version: string
  platform: string
  colorScheme: 'light' | 'dark'
  themeParams: {
    bg_color?: string
    text_color?: string
    hint_color?: string
    link_color?: string
    button_color?: string
    button_text_color?: string
  }
  backgroundColor: string
  MainButton: {
    text: string
    color: string
    textColor: string
    isVisible: boolean
    isActive: boolean
    setText: (text: string) => void
    onClick: (callback: () => void) => void
    show: () => void
    hide: () => void
  }
  BackButton: {
    isVisible: boolean
    onClick: (callback: () => void) => void
    show: () => void
    hide: () => void
  }
  showAlert: (message: string) => void
  showConfirm: (message: string, callback: (confirmed: boolean) => void) => void
}

declare global {
  interface Window {
    Telegram?: {
      WebApp: TelegramWebApp
    }
  }
}

export function useTelegram() {
  const [webApp, setWebApp] = useState<TelegramWebApp | null>(null)

  useEffect(() => {
    // Проверяем сразу
    const tg = window.Telegram?.WebApp
    if (tg) {
      setWebApp(tg)
    } else {
      // Если не найдено сразу - ждем немного и проверяем снова
      // Telegram SDK может загружаться асинхронно
      const checkInterval = setInterval(() => {
        const tgCheck = window.Telegram?.WebApp
        if (tgCheck) {
          setWebApp(tgCheck)
          clearInterval(checkInterval)
        }
      }, 100)
      
      // Останавливаем проверку через 2 секунды
      setTimeout(() => clearInterval(checkInterval), 2000)
    }
  }, [])

  // НЕ возвращаем объект user напрямую - это может вызвать ошибку React #301
  // Если нужны данные пользователя - используйте webApp.initDataUnsafe.user напрямую
  return {
    webApp,
    initData: webApp?.initData || '',
  }
}

