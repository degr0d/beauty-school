/**
 * Страница аналитики (только для админов)
 */

import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import axios from 'axios'

// API базовый URL
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

interface UserStats {
  total_users: number
  new_today: number
  new_week: number
  active_users: number
}

interface CourseStats {
  total_courses: number
  active_courses: number
  total_enrollments: number
  completed_courses: number
}

interface RevenueStats {
  total_revenue: number
  revenue_today: number
  revenue_week: number
  revenue_month: number
  total_payments: number
  successful_payments: number
}

interface ConversionFunnel {
  visitors: number
  registered: number
  purchased: number
  started_learning: number
  completed_course: number
}

interface DailyStat {
  date: string
  new_users: number
  new_enrollments: number
  completed_lessons: number
  revenue: number
}

interface CourseAnalytics {
  course_id: number
  course_title: string
  enrollments: number
  completions: number
  completion_rate: number
  average_progress: number
  revenue: number
}

const AnalyticsPage = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [userStats, setUserStats] = useState<UserStats | null>(null)
  const [courseStats, setCourseStats] = useState<CourseStats | null>(null)
  const [revenueStats, setRevenueStats] = useState<RevenueStats | null>(null)
  const [funnel, setFunnel] = useState<ConversionFunnel | null>(null)
  const [dailyStats, setDailyStats] = useState<DailyStat[]>([])
  const [coursesAnalytics, setCoursesAnalytics] = useState<CourseAnalytics[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadAnalytics()
  }, [])

  const loadAnalytics = async () => {
    try {
      setLoading(true)
      setError(null)

      // Загружаем все данные параллельно
      const [usersRes, coursesRes, revenueRes, funnelRes, dailyRes, coursesRes2] = await Promise.all([
        axios.get(`${API_BASE_URL}/analytics/stats/users`, {
          headers: {
            'X-Telegram-Init-Data': window.Telegram?.WebApp?.initData || '',
            'X-Telegram-User-ID': localStorage.getItem('dev_telegram_id') || ''
          }
        }),
        axios.get(`${API_BASE_URL}/analytics/stats/courses`, {
          headers: {
            'X-Telegram-Init-Data': window.Telegram?.WebApp?.initData || '',
            'X-Telegram-User-ID': localStorage.getItem('dev_telegram_id') || ''
          }
        }),
        axios.get(`${API_BASE_URL}/analytics/stats/revenue`, {
          headers: {
            'X-Telegram-Init-Data': window.Telegram?.WebApp?.initData || '',
            'X-Telegram-User-ID': localStorage.getItem('dev_telegram_id') || ''
          }
        }),
        axios.get(`${API_BASE_URL}/analytics/funnel`, {
          headers: {
            'X-Telegram-Init-Data': window.Telegram?.WebApp?.initData || '',
            'X-Telegram-User-ID': localStorage.getItem('dev_telegram_id') || ''
          }
        }),
        axios.get(`${API_BASE_URL}/analytics/daily?days=30`, {
          headers: {
            'X-Telegram-Init-Data': window.Telegram?.WebApp?.initData || '',
            'X-Telegram-User-ID': localStorage.getItem('dev_telegram_id') || ''
          }
        }),
        axios.get(`${API_BASE_URL}/analytics/courses`, {
          headers: {
            'X-Telegram-Init-Data': window.Telegram?.WebApp?.initData || '',
            'X-Telegram-User-ID': localStorage.getItem('dev_telegram_id') || ''
          }
        })
      ])

      setUserStats(usersRes.data)
      setCourseStats(coursesRes.data)
      setRevenueStats(revenueRes.data)
      setFunnel(funnelRes.data)
      setDailyStats(dailyRes.data || [])
      setCoursesAnalytics(coursesRes2.data || [])
    } catch (err: any) {
      console.error('Ошибка загрузки аналитики:', err)
      if (err.response?.status === 403) {
        setError('Доступ запрещен. Только для администраторов.')
      } else {
        setError('Ошибка загрузки данных аналитики')
      }
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="analytics-page" style={{ padding: '20px' }}>
        <div className="loading">Загрузка аналитики...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="analytics-page" style={{ padding: '20px' }}>
        <div className="error">
          <h2>❌ Ошибка</h2>
          <p>{error}</p>
          <button onClick={() => navigate('/')} style={{
            marginTop: '20px',
            padding: '10px 20px',
            backgroundColor: '#e91e63',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer'
          }}>
            Вернуться на главную
          </button>
        </div>
      </div>
    )
  }

  // Подготовка данных для графиков
  const funnelData = funnel ? [
    { name: 'Посетители', value: funnel.visitors },
    { name: 'Зарегистрированные', value: funnel.registered },
    { name: 'Купившие', value: funnel.purchased },
    { name: 'Начали обучение', value: funnel.started_learning },
    { name: 'Завершили курс', value: funnel.completed_course }
  ] : []

  const topCoursesData = coursesAnalytics
    .sort((a, b) => b.enrollments - a.enrollments)
    .slice(0, 5)
    .map(c => ({
      name: c.course_title.length > 20 ? c.course_title.substring(0, 20) + '...' : c.course_title,
      enrollments: c.enrollments,
      completions: c.completions
    }))

  return (
    <div className="analytics-page" style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1 style={{ marginBottom: '30px' }}>📊 Аналитика</h1>

      {/* Общая статистика */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '30px' }}>
        {userStats && (
          <div style={{ padding: '20px', backgroundColor: '#f9f9f9', borderRadius: '12px' }}>
            <h3 style={{ marginBottom: '15px', color: '#e91e63' }}>👥 Пользователи</h3>
            <div style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '5px' }}>{userStats.total_users}</div>
            <div style={{ fontSize: '14px', color: '#666' }}>
              Новых сегодня: {userStats.new_today}<br />
              Новых за неделю: {userStats.new_week}<br />
              Активных: {userStats.active_users}
            </div>
          </div>
        )}

        {courseStats && (
          <div style={{ padding: '20px', backgroundColor: '#f9f9f9', borderRadius: '12px' }}>
            <h3 style={{ marginBottom: '15px', color: '#9c27b0' }}>📚 Курсы</h3>
            <div style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '5px' }}>{courseStats.active_courses}</div>
            <div style={{ fontSize: '14px', color: '#666' }}>
              Всего: {courseStats.total_courses}<br />
              Записей: {courseStats.total_enrollments}<br />
              Завершено: {courseStats.completed_courses}
            </div>
          </div>
        )}

        {revenueStats && (
          <div style={{ padding: '20px', backgroundColor: '#f9f9f9', borderRadius: '12px' }}>
            <h3 style={{ marginBottom: '15px', color: '#4caf50' }}>💰 Выручка</h3>
            <div style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '5px' }}>
              {Math.round(revenueStats.total_revenue).toLocaleString('ru-RU')} ₽
            </div>
            <div style={{ fontSize: '14px', color: '#666' }}>
              Сегодня: {Math.round(revenueStats.revenue_today).toLocaleString('ru-RU')} ₽<br />
              За неделю: {Math.round(revenueStats.revenue_week).toLocaleString('ru-RU')} ₽<br />
              За месяц: {Math.round(revenueStats.revenue_month).toLocaleString('ru-RU')} ₽
            </div>
          </div>
        )}
      </div>

      {/* Воронка конверсии */}
      {funnel && (
        <div style={{ marginBottom: '30px', padding: '20px', backgroundColor: 'white', borderRadius: '12px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
          <h2 style={{ marginBottom: '20px' }}>📈 Воронка конверсии</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={funnelData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#e91e63" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Статистика по дням */}
      {dailyStats.length > 0 && (
        <div style={{ marginBottom: '30px', padding: '20px', backgroundColor: 'white', borderRadius: '12px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
          <h2 style={{ marginBottom: '20px' }}>📅 Статистика за последние 30 дней</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={dailyStats}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="date" 
                tick={{ fontSize: 12 }}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="new_users" stroke="#e91e63" name="Новые пользователи" />
              <Line type="monotone" dataKey="new_enrollments" stroke="#9c27b0" name="Новые записи" />
              <Line type="monotone" dataKey="completed_lessons" stroke="#4caf50" name="Завершенные уроки" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Топ курсов */}
      {topCoursesData.length > 0 && (
        <div style={{ marginBottom: '30px', padding: '20px', backgroundColor: 'white', borderRadius: '12px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
          <h2 style={{ marginBottom: '20px' }}>🔥 Топ-5 популярных курсов</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={topCoursesData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="enrollments" fill="#e91e63" name="Записей" />
              <Bar dataKey="completions" fill="#4caf50" name="Завершено" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Детальная статистика по курсам */}
      {coursesAnalytics.length > 0 && (
        <div style={{ padding: '20px', backgroundColor: 'white', borderRadius: '12px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
          <h2 style={{ marginBottom: '20px' }}>📊 Детальная статистика по курсам</h2>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: '#f5f5f5' }}>
                  <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #e0e0e0' }}>Курс</th>
                  <th style={{ padding: '12px', textAlign: 'center', borderBottom: '2px solid #e0e0e0' }}>Записей</th>
                  <th style={{ padding: '12px', textAlign: 'center', borderBottom: '2px solid #e0e0e0' }}>Завершено</th>
                  <th style={{ padding: '12px', textAlign: 'center', borderBottom: '2px solid #e0e0e0' }}>% Завершения</th>
                  <th style={{ padding: '12px', textAlign: 'center', borderBottom: '2px solid #e0e0e0' }}>Средний прогресс</th>
                  <th style={{ padding: '12px', textAlign: 'center', borderBottom: '2px solid #e0e0e0' }}>Выручка</th>
                </tr>
              </thead>
              <tbody>
                {coursesAnalytics.map((course) => (
                  <tr key={course.course_id} style={{ borderBottom: '1px solid #e0e0e0' }}>
                    <td style={{ padding: '12px' }}>{course.course_title}</td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>{course.enrollments}</td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>{course.completions}</td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>{course.completion_rate.toFixed(1)}%</td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>{course.average_progress.toFixed(1)}%</td>
                    <td style={{ padding: '12px', textAlign: 'center', fontWeight: 'bold', color: '#4caf50' }}>
                      {Math.round(course.revenue).toLocaleString('ru-RU')} ₽
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

export default AnalyticsPage

