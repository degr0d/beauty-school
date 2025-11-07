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
      const rawStatus = response.data
      
      // Нормализуем статус платежа - гарантируем что все поля это примитивы
      if (rawStatus) {
        const normalizedStatus: PaymentStatus = {
          payment_id: typeof rawStatus.payment_id === 'number' && !isNaN(rawStatus.payment_id) ? rawStatus.payment_id : 0,
          status: typeof rawStatus.status === 'string' ? rawStatus.status : 'pending',
          amount: typeof rawStatus.amount === 'number' && !isNaN(rawStatus.amount) ? rawStatus.amount : 0,
          course_id: typeof rawStatus.course_id === 'number' && !isNaN(rawStatus.course_id) ? rawStatus.course_id : 0
        }
        setStatus(normalizedStatus)
        
        // Загружаем информацию о курсе
        if (normalizedStatus.course_id) {
          const courseResponse = await coursesApi.getById(normalizedStatus.course_id)
          const rawCourse = courseResponse.data
          
          // Нормализуем курс
          if (rawCourse) {
            const normalizedCourse: CourseDetail = {
              id: typeof rawCourse.id === 'number' && !isNaN(rawCourse.id) ? rawCourse.id : 0,
              title: typeof rawCourse.title === 'string' ? rawCourse.title : 'Без названия',
              description: typeof rawCourse.description === 'string' ? rawCourse.description : '',
              category: typeof rawCourse.category === 'string' ? rawCourse.category : '',
              cover_image_url: typeof rawCourse.cover_image_url === 'string' && rawCourse.cover_image_url.trim() !== '' ? rawCourse.cover_image_url : undefined,
              is_top: rawCourse.is_top === true,
              price: typeof rawCourse.price === 'number' && !isNaN(rawCourse.price) ? rawCourse.price : 0,
              duration_hours: typeof rawCourse.duration_hours === 'number' && !isNaN(rawCourse.duration_hours) && rawCourse.duration_hours > 0 ? rawCourse.duration_hours : undefined,
              full_description: typeof rawCourse.full_description === 'string' ? rawCourse.full_description : undefined,
              lessons: Array.isArray(rawCourse.lessons) ? rawCourse.lessons.map((lesson: any) => ({
                id: typeof lesson?.id === 'number' && !isNaN(lesson.id) ? lesson.id : 0,
                title: typeof lesson?.title === 'string' ? lesson.title : 'Без названия',
                order: typeof lesson?.order === 'number' && !isNaN(lesson.order) ? lesson.order : 0,
                video_duration: typeof lesson?.video_duration === 'number' && !isNaN(lesson.video_duration) && lesson.video_duration > 0 ? lesson.video_duration : undefined,
                is_free: lesson?.is_free === true
              })) : []
            }
            setCourse(normalizedCourse)
          }
        }
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

