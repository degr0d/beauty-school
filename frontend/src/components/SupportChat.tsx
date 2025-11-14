/**
 * Компонент чата поддержки
 */

import { useEffect, useState, useRef } from 'react'
import { supportApi, type SupportTicket } from '../api/client'

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

  const loadTicket = async () => {
    try {
      setLoading(true)
      const response = await supportApi.getMyTicket()
      setTicket(response.data)
    } catch (error) {
      console.error('Ошибка загрузки тикета:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSendMessage = async () => {
    if (!message.trim() || sending) return

    try {
      setSending(true)
      const response = await supportApi.sendMessage({ message: message.trim() })
      
      // Обновляем тикет
      if (ticket) {
        setTicket({
          ...ticket,
          messages: [...ticket.messages, response.data],
          updated_at: new Date().toISOString()
        })
      }
      
      setMessage('')
    } catch (error: any) {
      console.error('Ошибка отправки сообщения:', error)
      const errorMessage = error.response?.data?.detail || 'Ошибка при отправке сообщения'
      if (window.Telegram?.WebApp) {
        window.Telegram.WebApp.showAlert(`Ошибка: ${errorMessage}`)
      } else {
        alert(`Ошибка: ${errorMessage}`)
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
            onClick={handleSendMessage}
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

