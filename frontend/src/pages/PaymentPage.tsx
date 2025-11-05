/**
 * Страница оплаты курса
 */

import { useEffect, useState } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { paymentApi, coursesApi, type PaymentStatus, type CourseDetail } from '../api/client'

const PaymentPage = () => {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const paymentId = searchParams.get('payment_id')
  const [status, setStatus] = useState<PaymentStatus | null>(null)
  const [course, setCourse] = useState<CourseDetail | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (paymentId) {
      checkPaymentStatus(parseInt(paymentId))
    } else {
      setLoading(false)
    }
  }, [paymentId])

  const checkPaymentStatus = async (id: number) => {
    try {
      const response = await paymentApi.getStatus(id)
      setStatus(response.data)
      
      // Загружаем информацию о курсе
      if (response.data.course_id) {
        const courseResponse = await coursesApi.getById(response.data.course_id)
        setCourse(courseResponse.data)
      }
    } catch (error) {
      console.error('Ошибка проверки статуса платежа:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="loading">Проверка статуса оплаты...</div>
  }

  if (!status) {
    return (
      <div className="payment-page">
        <div className="error">
          <h2>Платеж не найден</h2>
          <button onClick={() => navigate('/')} className="btn">
            Вернуться на главную
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="payment-page">
      <div className="payment-status">
        {status.status === 'succeeded' ? (
          <>
            <div className="success-icon">✅</div>
            <h1>Оплата успешна!</h1>
            {course && (
              <p>Курс "{course.title}" успешно приобретён</p>
            )}
            <p className="payment-amount">Сумма: {status.amount} ₽</p>
            <button 
              onClick={() => navigate(`/courses/${status.course_id}`)}
              className="btn"
            >
              Перейти к курсу
            </button>
          </>
        ) : status.status === 'pending' ? (
          <>
            <div className="pending-icon">⏳</div>
            <h1>Ожидание оплаты</h1>
            <p>Платеж обрабатывается...</p>
            <button 
              onClick={() => paymentId && checkPaymentStatus(parseInt(paymentId))}
              className="btn"
            >
              Обновить статус
            </button>
          </>
        ) : (
          <>
            <div className="error-icon">❌</div>
            <h1>Оплата отменена</h1>
            <p>Платеж был отменён</p>
            <button 
              onClick={() => navigate(`/courses/${status.course_id}`)}
              className="btn"
            >
              Вернуться к курсу
            </button>
          </>
        )}
      </div>
    </div>
  )
}

export default PaymentPage

