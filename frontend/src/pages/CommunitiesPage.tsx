/**
 * Страница сообществ/чатов с рулетками выбора
 */

import { useEffect, useState, useMemo } from 'react'
import { communitiesApi, type Community } from '../api/client'
import PickerWheel from '../components/PickerWheel'

const CommunitiesPage = () => {
  const [communities, setCommunities] = useState<Community[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedCityIndex, setSelectedCityIndex] = useState(0)
  const [selectedCategoryIndex, setSelectedCategoryIndex] = useState(0)
  const [selectedCommunity, setSelectedCommunity] = useState<Community | null>(null)

  useEffect(() => {
    loadCommunities()
  }, [])

  const loadCommunities = async () => {
    try {
      const response = await communitiesApi.getAll()
      const rawCommunities = Array.isArray(response.data) ? response.data : []
      const normalizedCommunities = rawCommunities.map(community => ({
        id: typeof community?.id === 'number' && !isNaN(community.id) ? community.id : 0,
        title: typeof community?.title === 'string' ? community.title : 'Без названия',
        description: typeof community?.description === 'string' && community.description.trim() !== '' ? community.description : undefined,
        type: typeof community?.type === 'string' && (community.type === 'city' || community.type === 'profession') ? community.type : 'city',
        city: typeof community?.city === 'string' && community.city.trim() !== '' ? community.city : undefined,
        category: typeof community?.category === 'string' && community.category.trim() !== '' ? community.category : undefined,
        telegram_link: typeof community?.telegram_link === 'string' && community.telegram_link.trim() !== '' ? community.telegram_link : ''
      }))
      setCommunities(normalizedCommunities)
    } catch (error) {
      console.error('Ошибка загрузки сообществ:', error)
      setCommunities([])
    } finally {
      setLoading(false)
    }
  }

  // Получаем уникальные города и категории
  const cities = useMemo(() => {
    const citySet = new Set<string>()
    communities.forEach(c => {
      if (c.city && c.type === 'city') {
        citySet.add(c.city)
      }
    })
    return Array.from(citySet).sort()
  }, [communities])

  const categories = useMemo(() => {
    // Получаем уникальные категории из сообществ
    const categorySet = new Set<string>()
    communities.forEach(c => {
      if (c.category && c.type === 'profession') {
        categorySet.add(c.category)
      }
    })
    
    // Маппинг категорий на красивые названия
    const categoryLabels: Record<string, string> = {
      'Маникюр и педикюр': '💅 Маникюр и педикюр',
      'Ресницы и брови': '👁 Ресницы и брови',
      'Своё дело': '💼 Своё дело',
      'manicure': '💅 Маникюр',
      'pedicure': '🦶 Педикюр',
      'eyelashes': '👁 Ресницы',
      'eyebrows': '🎨 Брови',
      'podology': '🩺 Подология',
      'marketing': '📢 Маркетинг',
      'business': '💼 Своё дело'
    }
    
    // Преобразуем категории в красивые названия
    const categoryList = Array.from(categorySet).map(cat => {
      return categoryLabels[cat] || cat
    }).sort()
    
    // Если нет категорий - добавляем стандартные
    if (categoryList.length === 0) {
      return ['💅 Маникюр и педикюр', '👁 Ресницы и брови', '💼 Своё дело']
    }
    
    return categoryList
  }, [communities])

  // Ищем сообщество по выбранным параметрам
  useEffect(() => {
    if (cities.length === 0 || categories.length === 0) {
      setSelectedCommunity(null)
      return
    }

    const selectedCity = cities[selectedCityIndex]
    const selectedCategoryLabel = categories[selectedCategoryIndex]
    
    // Обратный маппинг: из красивого названия в ключ категории
    const categoryKeyMap: Record<string, string> = {
      '💅 Маникюр и педикюр': 'Маникюр и педикюр',
      '👁 Ресницы и брови': 'Ресницы и брови',
      '💼 Своё дело': 'Своё дело',
      '💅 Маникюр': 'manicure',
      '🦶 Педикюр': 'pedicure',
      '👁 Ресницы': 'eyelashes',
      '🎨 Брови': 'eyebrows',
      '🩺 Подология': 'podology',
      '📢 Маркетинг': 'marketing'
    }
    
    // Получаем ключ категории (убираем эмодзи и пробелы для поиска)
    const categoryKey = categoryKeyMap[selectedCategoryLabel] || 
                       selectedCategoryLabel.replace(/^[^\s]+\s/, '').trim()

    // Ищем сообщество по городу (приоритет)
    let found = communities.find(c => 
      c.type === 'city' && 
      c.city === selectedCity
    )

    // Если не нашли по городу - ищем по категории
    if (!found) {
      found = communities.find(c => {
        if (c.type !== 'profession' || !c.category) return false
        
        // Сравниваем категории (учитываем разные форматы)
        const cCategory = c.category.toLowerCase().trim()
        const searchCategory = categoryKey.toLowerCase().trim()
        
        return cCategory === searchCategory || 
               cCategory.includes(searchCategory) || 
               searchCategory.includes(cCategory) ||
               c.category === categoryKey
      })
    }

    setSelectedCommunity(found || null)
  }, [selectedCityIndex, selectedCategoryIndex, cities, categories, communities])

  const openChat = (link: string) => {
    if (link) {
      window.open(link, '_blank')
    } else {
      if (window.Telegram?.WebApp) {
        window.Telegram.WebApp.showAlert('Ссылка на чат не указана')
      } else {
        alert('Ссылка на чат не указана')
      }
    }
  }

  if (loading) {
    return (
      <div className="communities-page" style={{ padding: '20px', textAlign: 'center' }}>
        <div className="loading">Загрузка сообществ...</div>
      </div>
    )
  }

  // Если нет городов или категорий - показываем старый интерфейс
  if (cities.length === 0 && categories.length === 0) {
    const cityCommunities = communities.filter(c => c.type === 'city')
    const professionCommunities = communities.filter(c => c.type === 'profession')

    return (
      <div className="communities-page">
        <h1>💬 Сообщества</h1>
        <p className="page-description">
          Вступай в чаты, общайся с коллегами и обменивайся опытом!
        </p>

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

        {communities.length === 0 && (
          <div className="empty-state">
            <p>Сообществ пока нет</p>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="communities-page" style={{ padding: '20px' }}>
      <h1 style={{ marginBottom: '10px' }}>💬 Сообщества</h1>
      <p style={{ marginBottom: '30px', color: '#666', fontSize: '14px' }}>
        Выберите город и направление, чтобы найти подходящий чат
      </p>

      {/* Рулетки выбора */}
      <div style={{
        display: 'flex',
        gap: '20px',
        marginBottom: '40px',
        minHeight: '280px'
      }}>
        {/* Рулетка городов */}
        <PickerWheel
          items={cities.length > 0 ? cities : ['Нет городов']}
          selectedIndex={selectedCityIndex}
          onSelect={setSelectedCityIndex}
          label="Город"
        />

        {/* Рулетка категорий */}
        <PickerWheel
          items={categories.length > 0 ? categories : ['Нет направлений']}
          selectedIndex={selectedCategoryIndex}
          onSelect={setSelectedCategoryIndex}
          label="Направление"
        />
      </div>

      {/* Результат выбора */}
      {selectedCommunity ? (
        <div style={{
          padding: '20px',
          backgroundColor: '#f9f9f9',
          borderRadius: '12px',
          border: '2px solid #e91e63',
          textAlign: 'center'
        }}>
          <h2 style={{ margin: '0 0 10px 0', color: '#e91e63' }}>
            {selectedCommunity.title}
          </h2>
          {selectedCommunity.description && (
            <p style={{ margin: '0 0 20px 0', color: '#666' }}>
              {selectedCommunity.description}
            </p>
          )}
          <button
            onClick={() => openChat(selectedCommunity.telegram_link)}
            style={{
              padding: '15px 40px',
              backgroundColor: '#e91e63',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '18px',
              fontWeight: 'bold',
              cursor: 'pointer',
              boxShadow: '0 4px 12px rgba(233, 30, 99, 0.3)',
              transition: 'all 0.3s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#c2185b'
              e.currentTarget.style.transform = 'translateY(-2px)'
              e.currentTarget.style.boxShadow = '0 6px 16px rgba(233, 30, 99, 0.4)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#e91e63'
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(233, 30, 99, 0.3)'
            }}
          >
            Вступить в чат
          </button>
        </div>
      ) : (
        <div style={{
          padding: '40px 20px',
          textAlign: 'center',
          color: '#999',
          backgroundColor: '#f5f5f5',
          borderRadius: '12px'
        }}>
          <p style={{ margin: 0, fontSize: '16px' }}>
            {cities.length === 0 && categories.length === 0
              ? 'Сообществ пока нет'
              : 'Выберите город и направление, чтобы найти чат'}
          </p>
        </div>
      )}
    </div>
  )
}

export default CommunitiesPage
