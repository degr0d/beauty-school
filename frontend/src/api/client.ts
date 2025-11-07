/**
 * API клиент для взаимодействия с backend
 */

import axios from 'axios'

// URL backend API
// Пробуем использовать переменную окружения, иначе относительный путь (проксирование через Vite)
// Если переменная не задана, используем относительный путь - Vite проксирует на backend
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

// Создаём axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Добавляем interceptor для автоматической отправки Telegram initData
api.interceptors.request.use((config) => {
  const webApp = window.Telegram?.WebApp
  if (webApp?.initData) {
    // Режим продакшена: используем реальный Telegram initData
    config.headers['X-Telegram-Init-Data'] = webApp.initData
    console.log('📤 [API] Отправка запроса с initData:', {
      url: config.url,
      hasInitData: !!webApp.initData,
      telegramId: webApp.initDataUnsafe?.user?.id
    })
  } else {
    // Режим разработки: используем заголовок X-Telegram-User-ID для локального тестирования
    const devTelegramId = localStorage.getItem('dev_telegram_id')
    if (devTelegramId) {
      config.headers['X-Telegram-User-ID'] = devTelegramId
      console.log('🔧 [DEV MODE] Используем dev_telegram_id из localStorage:', devTelegramId)
    } else {
      // Пробуем получить из переменной окружения или используем дефолтный админский ID
      const defaultDevId = import.meta.env.VITE_DEV_TELEGRAM_ID || '310836227' // Ваш админский ID
      config.headers['X-Telegram-User-ID'] = defaultDevId
      console.log('🔧 [DEV MODE] Используем дефолтный telegram_id:', defaultDevId)
      console.log('💡 [DEV MODE] Чтобы использовать другой ID, выполните в консоли:')
      console.log('   localStorage.setItem("dev_telegram_id", "YOUR_TELEGRAM_ID")')
    }
    console.warn('⚠️ [API] Запрос без initData (режим разработки):', config.url)
  }
  return config
}, (error) => {
  console.error('Ошибка запроса API:', error)
  return Promise.reject(error)
})

// Добавляем interceptor для обработки ошибок ответов
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('Ошибка ответа API:', error.response?.status, error.response?.data || error.message)
    // Не блокируем приложение при ошибках API
    return Promise.reject(error)
  }
)

// ========================================
// Courses API
// ========================================

export interface Course {
  id: number
  title: string
  description: string
  category: string
  cover_image_url?: string
  is_top: boolean
  price: number
  duration_hours?: number
}

export interface CourseDetail extends Course {
  full_description?: string
  lessons: Lesson[]
}

export interface Lesson {
  id: number
  title: string
  order: number
  video_duration?: number
  is_free: boolean
}

export interface LessonDetail extends Lesson {
  course_id: number
  description?: string
  video_url?: string
  pdf_url?: string
}

export const coursesApi = {
  // Получить все курсы
  getAll: (params?: { category?: string; is_top?: boolean }) =>
    api.get<Course[]>('/courses', { params }),

  // Получить курс по ID
  getById: (id: number) =>
    api.get<CourseDetail>(`/courses/${id}`),

  // Получить курсы пользователя
  getMy: () =>
    api.get<Course[]>('/courses/my/courses'),
}

// ========================================
// Lessons API
// ========================================

export const lessonsApi = {
  // Получить урок по ID
  getById: (id: number) =>
    api.get<LessonDetail>(`/lessons/${id}`),

  // Отметить урок как пройденный
  complete: (id: number) =>
    api.post(`/lessons/${id}/complete`),
}

// ========================================
// Profile API
// ========================================

export interface Profile {
  id: number
  telegram_id: number
  username?: string
  full_name: string
  phone: string
  email?: string
  city?: string
  points: number
  created_at: string
}

export const profileApi = {
  // Получить профиль
  get: () =>
    api.get<Profile>('/profile'),

  // Обновить профиль
  update: (data: { full_name?: string; phone?: string; email?: string; city?: string }) =>
    api.put<Profile>('/profile', data),
}

// ========================================
// Progress API
// ========================================

export interface CourseProgress {
  course_id: number
  course_title: string
  total_lessons: number
  completed_lessons: number
  progress_percent: number
  lessons: Array<{
    id: number
    title: string
    order: number
    completed: boolean
  }>
}

export const progressApi = {
  // Получить прогресс по курсу
  getByCourse: (courseId: number) =>
    api.get<CourseProgress>(`/progress/${courseId}`),

  // Получить общий прогресс
  getOverall: () =>
    api.get('/progress'),
}

// ========================================
// Communities API
// ========================================

export interface Community {
  id: number
  title: string
  description?: string
  type: 'city' | 'profession'
  city?: string
  category?: string
  telegram_link: string
}

export const communitiesApi = {
  // Получить все сообщества
  getAll: (params?: { type?: string; city?: string; category?: string }) =>
    api.get<Community[]>('/communities', { params }),

  // Получить сообщество по ID
  getById: (id: number) =>
    api.get<Community>(`/communities/${id}`),
}

// ========================================
// Payment API
// ========================================

export interface Payment {
  payment_id: number
  payment_url: string
  amount: number
  status: string
}

export interface PaymentStatus {
  payment_id: number
  status: string
  amount: number
  course_id: number
}

export interface PaymentHistoryItem {
  id: number
  course_id: number
  course_title: string
  amount: number
  status: string
  created_at: string
  paid_at?: string
}

export const paymentApi = {
  // Создать платеж
  create: (courseId: number) =>
    api.post<Payment>('/payment/create', { course_id: courseId }),
  
  // Получить статус платежа
  getStatus: (paymentId: number) =>
    api.get<PaymentStatus>(`/payment/status/${paymentId}`),
  
  // Получить историю платежей
  getHistory: () =>
    api.get<PaymentHistoryItem[]>('/payment/history'),
}

// ========================================
// Access API
// ========================================

export interface AccessStatus {
  has_access: boolean
  purchased_courses_count: number
  total_payments: number
}

export interface CourseAccessStatus {
  has_access: boolean
  course_id: number
  purchased_at?: string
}

export const accessApi = {
  // Проверить доступ к платформе
  checkAccess: () =>
    api.get<AccessStatus>('/access/check'),
  
  // Проверить доступ к курсу
  checkCourseAccess: (courseId: number) =>
    api.get<CourseAccessStatus>(`/access/check-course/${courseId}`),
}

export default api

