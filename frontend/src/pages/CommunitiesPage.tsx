/**
 * Страница сообществ/чатов
 */

import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { communitiesApi, type Community } from '../api/client'

const CommunitiesPage = () => {
  const navigate = useNavigate()
  const [communities, setCommunities] = useState<Community[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadCommunities()
  }, [])

  const loadCommunities = async () => {
    try {
      const response = await communitiesApi.getAll()
      // Гарантируем что это массив
      const rawCommunities = Array.isArray(response.data) ? response.data : []
      // Нормализуем все сообщества - гарантируем что все поля это примитивы
      const communities = rawCommunities.map(community => ({
        id: typeof community?.id === 'number' && !isNaN(community.id) ? community.id : 0,
        title: typeof community?.title === 'string' ? community.title : 'Без названия',
        description: typeof community?.description === 'string' && community.description.trim() !== '' ? community.description : undefined,
        type: typeof community?.type === 'string' && (community.type === 'city' || community.type === 'profession') ? community.type : 'city',
        city: typeof community?.city === 'string' && community.city.trim() !== '' ? community.city : undefined,
        category: typeof community?.category === 'string' && community.category.trim() !== '' ? community.category : undefined,
        telegram_link: typeof community?.telegram_link === 'string' && community.telegram_link.trim() !== '' ? community.telegram_link : ''
      }))
      setCommunities(communities)
    } catch (error) {
      console.error('Ошибка загрузки сообществ:', error)
      // Устанавливаем пустой массив при ошибке
      setCommunities([])
    } finally {
      setLoading(false)
    }
  }

  const openChat = (link: string) => {
    window.open(link, '_blank')
  }

  if (loading) {
    return <div className="loading">Загрузка сообществ...</div>
  }

  const cityCommunities = communities.filter(c => c.type === 'city')
  const professionCommunities = communities.filter(c => c.type === 'profession')

  return (
    <div className="communities-page">
      <h1>💬 Сообщества</h1>
      <p className="page-description">
        Вступай в чаты, общайся с коллегами и обменивайся опытом!
      </p>

      {/* Чаты по городам */}
      {cityCommunities.length > 0 && (
        <section className="communities-section">
          <h2>🌍 Чаты по городам</h2>
          <div className="communities-list">
            {cityCommunities.map(community => (
              <div key={community.id} className="community-card">
                <div className="community-info">
                  <h3>{community.title}</h3>
                  {community.description && <p>{community.description}</p>}
                </div>
                <button
                  className="join-btn"
                  onClick={() => openChat(community.telegram_link)}
                >
                  Вступить
                </button>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Чаты по профессиям */}
      {professionCommunities.length > 0 && (
        <section className="communities-section">
          <h2>💼 Чаты по направлениям</h2>
          <div className="communities-list">
            {professionCommunities.map(community => (
              <div key={community.id} className="community-card">
                <div className="community-info">
                  <h3>{community.title}</h3>
                  {community.description && <p>{community.description}</p>}
                </div>
                <button
                  className="join-btn"
                  onClick={() => openChat(community.telegram_link)}
                >
                  Вступить
                </button>
              </div>
            ))}
          </div>
        </section>
      )}

      {communities.length === 0 && !loading && (
        <div className="empty-state">
          <p>Сообществ пока нет</p>
        </div>
      )}
    </div>
  )
}

export default CommunitiesPage

