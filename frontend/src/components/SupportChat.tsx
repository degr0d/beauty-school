/**
 * Компонент чата поддержки
 */

import { useEffect, useState, useRef } from 'react'
import { supportApi, type SupportTicket, type SupportMessage } from '../api/client'

interface SupportChatProps {
  onClose: () => void
}

const SupportChat = ({ onClose }: SupportChatProps) => {
  const [ticket, setTicket] = useState<SupportTicket | null>(null)
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadTicket()
  }, [])

  useEffect(() => {
    // Прокрутка вниз при новых сообщениях
    scrollToBottom()
  }, [ticket?.messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const loadTicket = async (retryCount = 0) => {
    try {
      setLoading(true)
      console.log('💬 [SupportChat] Загрузка тикета...', retryCount > 0 ? `(попытка ${retryCount + 1})` : '')
      const response = await supportApi.getMyTicket()
      console.log('✅ [SupportChat] Тикет загружен:', response.data)
      setTicket(response.data)
    } catch (error: any) {
      console.error('❌ [SupportChat] Ошибка загрузки тикета:', error)
      console.error('   Тип ошибки:', error.constructor?.name || typeof error)
      console.error('   Сообщение:', error.message)
      console.error('   Статус:', error.response?.status)
      console.error('   Данные:', error.response?.data)
      
      // Если это Network Error и еще не было 2 попыток - пробуем еще раз
      if ((!error.response && (error.message?.includes('Network') || error.code === 'ERR_NETWORK')) && retryCount < 2) {
        console.warn(`⚠️ [SupportChat] Network Error, пробуем еще раз через ${(retryCount + 1) * 500}мс...`)
        await new Promise(resolve => setTimeout(resolve, (retryCount + 1) * 500))
        return loadTicket(retryCount + 1)
      }
      
      // Если это не критичная ошибка (например, тикет просто не найден) - продолжаем работу
      if (error.response?.status === 404) {
        console.log('ℹ️ [SupportChat] Тикет не найден, будет создан при отправке первого сообщения')
        setTicket(null)
        return
      }
      
      // Показываем ошибку только если это не Network Error (он уже обработан)
      if (error.response || (!error.message?.includes('Network') && error.code !== 'ERR_NETWORK')) {
        const errorMessage = error.response?.data?.detail || 
                            error.response?.data?.message || 
                            error.message || 
                            'Ошибка при загрузке чата поддержки'
        if (window.Telegram?.WebApp) {
          window.Telegram.WebApp.showAlert(`Ошибка: ${errorMessage}`)
        } else {
          alert(`Ошибка: ${errorMessage}`)
        }
      }
    } finally {
      setLoading(false)
    }
  }

  const handleSendMessage = async (retryCount = 0) => {
    if (!message.trim() || sending) return

    const messageText = message.trim()
    
    // Оптимистичное обновление UI - сразу показываем сообщение
    const tempMessage: SupportMessage = {
      id: Date.now(), // Временный ID
      ticket_id: ticket?.id || 0,
      message: messageText,
      is_from_admin: false,
      created_at: new Date().toISOString()
    }
    
    // Добавляем сообщение в UI сразу
    if (ticket) {
      setTicket({
        ...ticket,
        messages: [...ticket.messages, tempMessage],
        updated_at: new Date().toISOString()
      })
    } else {
      // Если тикета нет - создаем временный
      setTicket({
        id: 0,
        status: 'open',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        messages: [tempMessage]
      })
    }
    
    const previousMessage = message
    setMessage('') // Очищаем поле ввода сразу
    setSending(true)

    try {
      console.log('💬 [SupportChat] Отправка сообщения:', messageText, retryCount > 0 ? `(попытка ${retryCount + 1})` : '')
      
      const response = await supportApi.sendMessage({ message: messageText })
      console.log('✅ [SupportChat] Сообщение отправлено:', response.data)
      
      // Обновляем тикет с реальными данными с сервера
      if (ticket) {
        // Заменяем временное сообщение на реальное
        const updatedMessages = ticket.messages.map(msg => 
          msg.id === tempMessage.id ? response.data : msg
        )
        setTicket({
          ...ticket,
          messages: updatedMessages,
          updated_at: new Date().toISOString()
        })
      } else {
        // Если тикета не было - перезагружаем его
        await loadTicket()
      }
    } catch (error: any) {
      console.error('❌ [SupportChat] Ошибка отправки сообщения:', error)
      console.error('   Тип ошибки:', error.constructor?.name || typeof error)
      console.error('   Сообщение:', error.message)
      console.error('   Статус:', error.response?.status)
      console.error('   Данные:', error.response?.data)
      console.error('   URL запроса:', error.config?.url)
      
      // Откатываем оптимистичное обновление
      if (ticket) {
        const updatedMessages = ticket.messages.filter(msg => msg.id !== tempMessage.id)
        setTicket({
          ...ticket,
          messages: updatedMessages,
          updated_at: new Date().toISOString()
        })
      } else {
        setTicket(null)
      }
      
      // Возвращаем текст сообщения в поле ввода
      setMessage(previousMessage)
      
      // Если это Network Error и еще не было 2 попыток - пробуем еще раз
      if ((!error.response && (error.message?.includes('Network') || error.code === 'ERR_NETWORK')) && retryCount < 2) {
        console.warn(`⚠️ [SupportChat] Network Error, пробуем еще раз через ${(retryCount + 1) * 500}мс...`)
        await new Promise(resolve => setTimeout(resolve, (retryCount + 1) * 500))
        return handleSendMessage(retryCount + 1)
      }
      
      // Показываем ошибку только если это не Network Error (он уже обработан)
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message || 
                          error.message || 
                          'Ошибка при отправке сообщения'
      
      if (error.response || (!error.message?.includes('Network') && error.code !== 'ERR_NETWORK')) {
        if (window.Telegram?.WebApp) {
          window.Telegram.WebApp.showAlert(`Ошибка: ${errorMessage}`)
        } else {
          alert(`Ошибка: ${errorMessage}`)
        }
      }
    } finally {
      setSending(false)
    }
  }

  if (loading) {
    return (
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000
      }}>
        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          padding: '20px',
          maxWidth: '90%',
          width: '400px'
        }}>
          <div>Загрузка...</div>
        </div>
      </div>
    )
  }

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '20px'
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        width: '100%',
        maxWidth: '500px',
        maxHeight: '80vh',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)'
      }}>
        {/* Заголовок */}
        <div style={{
          padding: '15px 20px',
          borderBottom: '1px solid #e0e0e0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 'bold' }}>
            💬 Поддержка
          </h2>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              fontSize: '24px',
              cursor: 'pointer',
              padding: '0',
              width: '30px',
              height: '30px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            ✕
          </button>
        </div>

        {/* Сообщения */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          padding: '20px',
          display: 'flex',
          flexDirection: 'column',
          gap: '15px'
        }}>
          {ticket && ticket.messages.length > 0 ? (
            ticket.messages.map((msg) => (
              <div
                key={msg.id}
                style={{
                  display: 'flex',
                  justifyContent: msg.is_from_admin ? 'flex-start' : 'flex-end',
                  marginBottom: '10px'
                }}
              >
                <div style={{
                  maxWidth: '75%',
                  padding: '12px 16px',
                  borderRadius: '12px',
                  backgroundColor: msg.is_from_admin ? '#f0f0f0' : '#e91e63',
                  color: msg.is_from_admin ? '#333' : 'white',
                  wordWrap: 'break-word'
                }}>
                  <div style={{ marginBottom: '5px', fontSize: '14px' }}>
                    {msg.message}
                  </div>
                  <div style={{
                    fontSize: '11px',
                    opacity: 0.7,
                    textAlign: 'right'
                  }}>
                    {new Date(msg.created_at).toLocaleTimeString('ru-RU', {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div style={{
              textAlign: 'center',
              color: '#666',
              padding: '40px 20px',
              fontSize: '14px'
            }}>
              Напишите ваш вопрос, и мы обязательно поможем! 💬
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Поле ввода */}
        <div style={{
          padding: '15px 20px',
          borderTop: '1px solid #e0e0e0',
          display: 'flex',
          gap: '10px'
        }}>
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSendMessage()
              }
            }}
            placeholder="Напишите сообщение..."
            disabled={sending}
            style={{
              flex: 1,
              padding: '12px 16px',
              border: '1px solid #e0e0e0',
              borderRadius: '8px',
              fontSize: '14px',
              outline: 'none'
            }}
          />
          <button
            onClick={() => handleSendMessage(0)}
            disabled={!message.trim() || sending}
            style={{
              padding: '12px 24px',
              backgroundColor: sending || !message.trim() ? '#ccc' : '#e91e63',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: 'bold',
              cursor: sending || !message.trim() ? 'not-allowed' : 'pointer'
            }}
          >
            {sending ? '⏳' : 'Отправить'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default SupportChat

