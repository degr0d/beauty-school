/**
 * Компонент секции отзывов и рейтингов
 */

import { useState, useEffect } from 'react'
import { reviewsApi, type Review, type CourseRating, type ReviewCreate } from '../api/client'

interface ReviewsSectionProps {
  courseId: number
}

const ReviewsSection = ({ courseId }: ReviewsSectionProps) => {
  const [reviews, setReviews] = useState<Review[]>([])
  const [rating, setRating] = useState<CourseRating | null>(null)
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [newRating, setNewRating] = useState(5)
  const [newComment, setNewComment] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [myReview, setMyReview] = useState<Review | null>(null)

  useEffect(() => {
    loadReviews()
    loadRating()
  }, [courseId])

  const loadReviews = async () => {
    try {
      const response = await reviewsApi.getByCourse(courseId, 20)
      setReviews(Array.isArray(response.data) ? response.data : [])
      
      // Проверяем, есть ли мой отзыв
      try {
        const myReviewsResponse = await reviewsApi.getMy()
        const myReviews = Array.isArray(myReviewsResponse.data) ? myReviewsResponse.data : []
        const myCourseReview = myReviews.find(r => r.course_id === courseId)
        setMyReview(myCourseReview || null)
      } catch (error) {
        // Игнорируем ошибки при загрузке своих отзывов
      }
    } catch (error) {
      console.error('Ошибка загрузки отзывов:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadRating = async () => {
    try {
      const response = await reviewsApi.getCourseRating(courseId)
      setRating(response.data)
    } catch (error) {
      console.error('Ошибка загрузки рейтинга:', error)
    }
  }

  const handleSubmitReview = async () => {
    if (submitting) return
    
    try {
      setSubmitting(true)
      const reviewData: ReviewCreate = {
        rating: newRating,
        comment: newComment.trim() || undefined
      }
      
      const response = await reviewsApi.create(courseId, reviewData)
      setMyReview(response.data)
      setShowForm(false)
      setNewComment('')
      
      // Перезагружаем отзывы и рейтинг
      await loadReviews()
      await loadRating()
    } catch (error) {
      console.error('Ошибка создания отзыва:', error)
      alert('Не удалось оставить отзыв. Попробуйте позже.')
    } finally {
      setSubmitting(false)
    }
  }

  const handleDeleteReview = async (reviewId: number) => {
    if (!confirm('Удалить отзыв?')) return
    
    try {
      await reviewsApi.delete(reviewId)
      setMyReview(null)
      await loadReviews()
      await loadRating()
    } catch (error) {
      console.error('Ошибка удаления отзыва:', error)
      alert('Не удалось удалить отзыв.')
    }
  }

  const renderStars = (ratingValue: number, interactive: boolean = false, onChange?: (rating: number) => void) => {
    return (
      <div style={{ display: 'flex', gap: '5px' }}>
        {[1, 2, 3, 4, 5].map((star) => (
          <span
            key={star}
            onClick={() => interactive && onChange && onChange(star)}
            style={{
              fontSize: '24px',
              cursor: interactive ? 'pointer' : 'default',
              color: star <= ratingValue ? '#ffc107' : '#e0e0e0'
            }}
          >
            ⭐
          </span>
        ))}
      </div>
    )
  }

  if (loading) {
    return <div style={{ padding: '20px', textAlign: 'center' }}>Загрузка отзывов...</div>
  }

  return (
    <div style={{ marginTop: '40px', padding: '20px', backgroundColor: '#f9f9f9', borderRadius: '12px' }}>
      <h2 style={{ marginBottom: '20px' }}>⭐ Отзывы и рейтинг</h2>

      {/* Рейтинг курса */}
      {rating && (
        <div style={{ marginBottom: '30px', padding: '20px', backgroundColor: 'white', borderRadius: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px', marginBottom: '15px' }}>
            <div>
              <div style={{ fontSize: '48px', fontWeight: 'bold', color: '#e91e63' }}>
                {rating.average_rating.toFixed(1)}
              </div>
              <div style={{ fontSize: '14px', color: '#666' }}>
                {renderStars(Math.round(rating.average_rating))}
              </div>
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: '16px', marginBottom: '10px' }}>
                Всего отзывов: <strong>{rating.total_reviews}</strong>
              </div>
              {/* Распределение рейтингов */}
              {[5, 4, 3, 2, 1].map((star) => {
                const count = rating.rating_distribution[star] || 0
                const percent = rating.total_reviews > 0 ? (count / rating.total_reviews) * 100 : 0
                return (
                  <div key={star} style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '5px' }}>
                    <span style={{ width: '60px' }}>{star} ⭐</span>
                    <div style={{ flex: 1, height: '8px', backgroundColor: '#e0e0e0', borderRadius: '4px', overflow: 'hidden' }}>
                      <div
                        style={{
                          width: `${percent}%`,
                          height: '100%',
                          backgroundColor: '#e91e63',
                          transition: 'width 0.3s ease'
                        }}
                      />
                    </div>
                    <span style={{ fontSize: '12px', color: '#666', width: '40px', textAlign: 'right' }}>
                      {count}
                    </span>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      )}

      {/* Форма создания отзыва */}
      {!myReview && (
        <div style={{ marginBottom: '30px' }}>
          {!showForm ? (
            <button
              onClick={() => setShowForm(true)}
              style={{
                padding: '12px 24px',
                backgroundColor: '#e91e63',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '16px',
                cursor: 'pointer',
                fontWeight: 'bold'
              }}
            >
              Оставить отзыв
            </button>
          ) : (
            <div style={{ padding: '20px', backgroundColor: 'white', borderRadius: '8px' }}>
              <h3 style={{ marginBottom: '15px' }}>Ваш отзыв</h3>
              
              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
                  Оценка:
                </label>
                {renderStars(newRating, true, setNewRating)}
              </div>

              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
                  Комментарий (необязательно):
                </label>
                <textarea
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  placeholder="Расскажите о вашем опыте..."
                  style={{
                    width: '100%',
                    minHeight: '100px',
                    padding: '12px',
                    border: '1px solid #e0e0e0',
                    borderRadius: '8px',
                    fontSize: '14px',
                    fontFamily: 'inherit',
                    resize: 'vertical'
                  }}
                  maxLength={2000}
                />
                <div style={{ fontSize: '12px', color: '#666', marginTop: '5px', textAlign: 'right' }}>
                  {newComment.length} / 2000
                </div>
              </div>

              <div style={{ display: 'flex', gap: '10px' }}>
                <button
                  onClick={handleSubmitReview}
                  disabled={submitting}
                  style={{
                    padding: '12px 24px',
                    backgroundColor: '#e91e63',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '16px',
                    cursor: submitting ? 'not-allowed' : 'pointer',
                    fontWeight: 'bold',
                    opacity: submitting ? 0.6 : 1
                  }}
                >
                  {submitting ? 'Отправка...' : 'Отправить'}
                </button>
                <button
                  onClick={() => {
                    setShowForm(false)
                    setNewComment('')
                    setNewRating(5)
                  }}
                  style={{
                    padding: '12px 24px',
                    backgroundColor: '#e0e0e0',
                    color: '#333',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '16px',
                    cursor: 'pointer'
                  }}
                >
                  Отмена
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Список отзывов */}
      <div>
        <h3 style={{ marginBottom: '15px' }}>
          Отзывы ({reviews.length})
        </h3>

        {reviews.length === 0 ? (
          <div style={{ padding: '40px', textAlign: 'center', color: '#666' }}>
            Пока нет отзывов. Будьте первым!
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            {reviews.map((review) => (
              <div
                key={review.id}
                style={{
                  padding: '20px',
                  backgroundColor: 'white',
                  borderRadius: '8px',
                  border: review.id === myReview?.id ? '2px solid #e91e63' : '1px solid #e0e0e0'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                  <div>
                    <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
                      {review.user_name}
                    </div>
                    <div style={{ fontSize: '14px', color: '#666' }}>
                      {new Date(review.created_at).toLocaleDateString('ru-RU')}
                    </div>
                  </div>
                  {review.id === myReview?.id && (
                    <button
                      onClick={() => handleDeleteReview(review.id)}
                      style={{
                        padding: '6px 12px',
                        backgroundColor: '#ff4444',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        fontSize: '12px',
                        cursor: 'pointer'
                      }}
                    >
                      Удалить
                    </button>
                  )}
                </div>
                
                <div style={{ marginBottom: '10px' }}>
                  {renderStars(review.rating)}
                </div>

                {review.comment && (
                  <div style={{ fontSize: '14px', lineHeight: '1.6', color: '#333' }}>
                    {review.comment}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default ReviewsSection


