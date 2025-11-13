/**
 * Страница лидборда (топ пользователей)
 */

import { useEffect, useState } from 'react'
import { leaderboardApi, type LeaderboardEntry, type MyPosition } from '../api/client'

const LeaderboardPage = () => {
  const [topByPoints, setTopByPoints] = useState<LeaderboardEntry[]>([])
  const [topByCourses, setTopByCourses] = useState<LeaderboardEntry[]>([])
  const [myPosition, setMyPosition] = useState<MyPosition | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'points' | 'courses'>('points')

  useEffect(() => {
    loadLeaderboard()
  }, [])

  const loadLeaderboard = async () => {
    try {
      setLoading(true)
      
      // Загружаем топ по баллам
      const pointsResponse = await leaderboardApi.getTop(20)
      setTopByPoints(Array.isArray(pointsResponse.data) ? pointsResponse.data : [])
      
      // Загружаем топ по курсам
      const coursesResponse = await leaderboardApi.getTopByCourses(20)
      setTopByCourses(Array.isArray(coursesResponse.data) ? coursesResponse.data : [])
      
      // Загружаем позицию пользователя
      try {
        const positionResponse = await leaderboardApi.getMyPosition()
        setMyPosition(positionResponse.data)
      } catch (error) {
        console.warn('Не удалось загрузить позицию пользователя:', error)
      }
    } catch (error) {
      console.error('Ошибка загрузки лидборда:', error)
    } finally {
      setLoading(false)
    }
  }

  const getMedal = (position: number) => {
    if (position === 1) return '🥇'
    if (position === 2) return '🥈'
    if (position === 3) return '🥉'
    return `#${position}`
  }

  if (loading) {
    return (
      <div className="leaderboard-page">
        <div className="loading">Загрузка лидборда...</div>
      </div>
    )
  }

  const currentList = activeTab === 'points' ? topByPoints : topByCourses

  return (
    <div className="leaderboard-page">
      <h1>🏆 Лидборд</h1>

      {/* Позиция пользователя */}
      {myPosition && (
        <div style={{
          padding: '15px',
          marginBottom: '20px',
          backgroundColor: '#f0f8ff',
          borderRadius: '8px',
          border: '1px solid #e0e0e0'
        }}>
          <h3 style={{ margin: '0 0 10px 0', color: '#333' }}>Ваша позиция</h3>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#e91e63' }}>
                #{myPosition.position} из {myPosition.total_users}
              </div>
              <div style={{ fontSize: '14px', color: '#666', marginTop: '5px' }}>
                {myPosition.points} баллов • {myPosition.completed_courses} курсов • {myPosition.completed_lessons} уроков
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Табы */}
      <div style={{
        display: 'flex',
        gap: '10px',
        marginBottom: '20px',
        borderBottom: '2px solid #e0e0e0'
      }}>
        <button
          onClick={() => setActiveTab('points')}
          style={{
            padding: '10px 20px',
            border: 'none',
            background: 'transparent',
            borderBottom: activeTab === 'points' ? '2px solid #e91e63' : '2px solid transparent',
            color: activeTab === 'points' ? '#e91e63' : '#666',
            fontWeight: activeTab === 'points' ? 'bold' : 'normal',
            cursor: 'pointer',
            fontSize: '16px'
          }}
        >
          💎 По баллам
        </button>
        <button
          onClick={() => setActiveTab('courses')}
          style={{
            padding: '10px 20px',
            border: 'none',
            background: 'transparent',
            borderBottom: activeTab === 'courses' ? '2px solid #e91e63' : '2px solid transparent',
            color: activeTab === 'courses' ? '#e91e63' : '#666',
            fontWeight: activeTab === 'courses' ? 'bold' : 'normal',
            cursor: 'pointer',
            fontSize: '16px'
          }}
        >
          📚 По курсам
        </button>
      </div>

      {/* Список лидборда */}
      {currentList.length > 0 ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {currentList.map((entry) => (
            <div
              key={entry.user_id}
              style={{
                padding: '15px',
                backgroundColor: entry.position <= 3 ? '#fff9e6' : '#f9f9f9',
                borderRadius: '8px',
                border: entry.position <= 3 ? '2px solid #ffd700' : '1px solid #e0e0e0',
                display: 'flex',
                alignItems: 'center',
                gap: '15px'
              }}
            >
              <div style={{
                fontSize: '24px',
                fontWeight: 'bold',
                minWidth: '50px',
                textAlign: 'center'
              }}>
                {getMedal(entry.position)}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 'bold', fontSize: '16px', marginBottom: '5px' }}>
                  {entry.full_name}
                </div>
                <div style={{ fontSize: '14px', color: '#666' }}>
                  {activeTab === 'points' ? (
                    <>💎 {entry.points} баллов • 📚 {entry.completed_courses} курсов • ✅ {entry.completed_lessons} уроков</>
                  ) : (
                    <>📚 {entry.completed_courses} курсов • 💎 {entry.points} баллов • ✅ {entry.completed_lessons} уроков</>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="empty-state">
          <p>Пока нет данных в лидборде</p>
        </div>
      )}
    </div>
  )
}

export default LeaderboardPage

