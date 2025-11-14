/**
 * Страница челленджей
 */

import { useEffect, useState } from 'react'
import { challengesApi, type Challenge } from '../api/client'

const ChallengesPage = () => {
  const [challenges, setChallenges] = useState<Challenge[]>([])
  const [myChallenges, setMyChallenges] = useState<Challenge[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'all' | 'my'>('all')

  useEffect(() => {
    loadChallenges()
  }, [])

  const loadChallenges = async () => {
    try {
      setLoading(true)
      
      // Загружаем все челленджи
      const allResponse = await challengesApi.getAll()
      setChallenges(Array.isArray(allResponse.data) ? allResponse.data : [])
      
      // Загружаем мои челленджи
      try {
        const myResponse = await challengesApi.getMy()
        setMyChallenges(Array.isArray(myResponse.data) ? myResponse.data : [])
      } catch (error) {
        console.warn('Не удалось загрузить мои челленджи:', error)
        setMyChallenges([])
      }
    } catch (error) {
      console.error('Ошибка загрузки челленджей:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleJoin = async (challengeId: number) => {
    try {
      await challengesApi.join(challengeId)
      await loadChallenges() // Перезагружаем список
    } catch (error: any) {
      console.error('Ошибка присоединения к челленджу:', error)
      alert(error.response?.data?.detail || 'Не удалось присоединиться к челленджу')
    }
  }

  const getConditionText = (challenge: Challenge) => {
    switch (challenge.condition_type) {
      case 'complete_lessons':
        return `Пройдите ${challenge.condition_value} уроков`
      case 'complete_courses':
        return `Завершите ${challenge.condition_value} курсов`
      case 'earn_points':
        return `Заработайте ${challenge.condition_value} баллов`
      default:
        return `Выполните условие: ${challenge.condition_type}`
    }
  }

  const getProgressPercent = (challenge: Challenge) => {
    if (!challenge.user_progress) return 0
    return Math.min((challenge.user_progress / challenge.condition_value) * 100, 100)
  }

  if (loading) {
    return (
      <div className="challenges-page">
        <div className="loading">Загрузка челленджей...</div>
      </div>
    )
  }

  const currentList = activeTab === 'all' ? challenges : myChallenges

  return (
    <div className="challenges-page">
      <h1>🎯 Челленджи</h1>

      {/* Табы */}
      <div style={{
        display: 'flex',
        gap: '10px',
        marginBottom: '20px',
        borderBottom: '2px solid #e0e0e0'
      }}>
        <button
          onClick={() => setActiveTab('all')}
          style={{
            padding: '10px 20px',
            border: 'none',
            background: 'transparent',
            borderBottom: activeTab === 'all' ? '2px solid #e91e63' : '2px solid transparent',
            color: activeTab === 'all' ? '#e91e63' : '#666',
            fontWeight: activeTab === 'all' ? 'bold' : 'normal',
            cursor: 'pointer',
            fontSize: '16px'
          }}
        >
          Все челленджи
        </button>
        <button
          onClick={() => setActiveTab('my')}
          style={{
            padding: '10px 20px',
            border: 'none',
            background: 'transparent',
            borderBottom: activeTab === 'my' ? '2px solid #e91e63' : '2px solid transparent',
            color: activeTab === 'my' ? '#e91e63' : '#666',
            fontWeight: activeTab === 'my' ? 'bold' : 'normal',
            cursor: 'pointer',
            fontSize: '16px'
          }}
        >
          Мои челленджи ({myChallenges.length})
        </button>
      </div>

      {/* Список челленджей */}
      {currentList.length > 0 ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {currentList.map((challenge) => {
            const progressPercent = getProgressPercent(challenge)
            const isExpired = challenge.end_date && new Date(challenge.end_date) < new Date()
            
            return (
              <div
                key={challenge.id}
                style={{
                  padding: '20px',
                  backgroundColor: challenge.user_completed ? '#e8f5e9' : '#f9f9f9',
                  borderRadius: '12px',
                  border: challenge.user_completed ? '2px solid #4caf50' : '1px solid #e0e0e0'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '15px', marginBottom: '15px' }}>
                  {challenge.icon_url ? (
                    <img
                      src={challenge.icon_url}
                      alt={challenge.title}
                      style={{ width: '60px', height: '60px', borderRadius: '8px' }}
                    />
                  ) : (
                    <div style={{
                      width: '60px',
                      height: '60px',
                      borderRadius: '8px',
                      backgroundColor: '#e91e63',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '30px'
                    }}>
                      🎯
                    </div>
                  )}
                  
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                      <h3 style={{ margin: 0, fontSize: '20px', fontWeight: 'bold' }}>
                        {challenge.title}
                      </h3>
                      {challenge.user_completed && (
                        <span style={{
                          padding: '4px 12px',
                          backgroundColor: '#4caf50',
                          color: 'white',
                          borderRadius: '12px',
                          fontSize: '12px',
                          fontWeight: 'bold'
                        }}>
                          ✅ Выполнено
                        </span>
                      )}
                    </div>
                    
                    <p style={{ margin: '0 0 10px 0', color: '#666', fontSize: '14px' }}>
                      {challenge.description}
                    </p>
                    
                    <div style={{ fontSize: '14px', color: '#666', marginBottom: '10px' }}>
                      <div>🎯 {getConditionText(challenge)}</div>
                      <div>💎 Награда: {challenge.points_reward} баллов</div>
                      {challenge.end_date && (
                        <div style={{ color: isExpired ? '#f44336' : '#666' }}>
                          ⏰ До {new Date(challenge.end_date).toLocaleDateString('ru-RU')}
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Прогресс */}
                {challenge.user_joined && (
                  <div style={{ marginTop: '15px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px', fontSize: '14px' }}>
                      <span>Прогресс:</span>
                      <span style={{ fontWeight: 'bold' }}>
                        {challenge.user_progress || 0} / {challenge.condition_value}
                      </span>
                    </div>
                    <div style={{
                      width: '100%',
                      height: '8px',
                      backgroundColor: '#e0e0e0',
                      borderRadius: '4px',
                      overflow: 'hidden'
                    }}>
                      <div
                        style={{
                          width: `${progressPercent}%`,
                          height: '100%',
                          backgroundColor: challenge.user_completed ? '#4caf50' : '#e91e63',
                          transition: 'width 0.3s ease'
                        }}
                      />
                    </div>
                  </div>
                )}

                {/* Кнопка присоединения */}
                {!challenge.user_joined && !isExpired && challenge.is_active && (
                  <button
                    onClick={() => handleJoin(challenge.id)}
                    style={{
                      marginTop: '15px',
                      width: '100%',
                      padding: '12px 20px',
                      backgroundColor: '#e91e63',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      fontSize: '16px',
                      fontWeight: 'bold',
                      cursor: 'pointer'
                    }}
                  >
                    Присоединиться
                  </button>
                )}
              </div>
            )
          })}
        </div>
      ) : (
        <div className="empty-state">
          <p>
            {activeTab === 'all' 
              ? 'Пока нет активных челленджей' 
              : 'Вы не участвуете ни в одном челлендже'}
          </p>
        </div>
      )}
    </div>
  )
}

export default ChallengesPage


