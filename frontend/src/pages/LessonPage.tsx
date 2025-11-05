/**
 * Страница урока (видео + материалы)
 */

import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { lessonsApi, accessApi, type LessonDetail } from '../api/client'

// Преобразование YouTube URL в embed формат
function getYouTubeEmbedUrl(url: string): string {
  // Поддержка разных форматов YouTube URL
  let videoId = ''
  
  if (url.includes('youtube.com/watch?v=')) {
    videoId = url.split('v=')[1]?.split('&')[0] || ''
  } else if (url.includes('youtu.be/')) {
    videoId = url.split('youtu.be/')[1]?.split('?')[0] || ''
  } else if (url.includes('youtube.com/embed/')) {
    videoId = url.split('embed/')[1]?.split('?')[0] || ''
  }
  
  if (!videoId) {
    // Если не удалось распарсить, возвращаем исходный URL
    return url
  }
  
  return `https://www.youtube.com/embed/${videoId}`
}

const LessonPage = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [lesson, setLesson] = useState<LessonDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [completed, setCompleted] = useState(false)
  const [accessDenied, setAccessDenied] = useState(false)

  useEffect(() => {
    if (id) {
      loadLesson(parseInt(id))
    }
  }, [id])

  const loadLesson = async (lessonId: number) => {
    try {
      const response = await lessonsApi.getById(lessonId)
      setLesson(response.data)
      
      // Проверяем доступ к курсу (если урок платный)
      if (!response.data.is_free && response.data.course_id) {
        try {
          const accessResponse = await accessApi.checkCourseAccess(response.data.course_id)
          if (!accessResponse.data.has_access) {
            setAccessDenied(true)
          }
        } catch (error) {
          console.error('Ошибка проверки доступа:', error)
          setAccessDenied(true)
        }
      }
    } catch (error: any) {
      console.error('Ошибка загрузки урока:', error)
      if (error.response?.status === 403) {
        setAccessDenied(true)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleCompleteLesson = async () => {
    if (!lesson) return

    try {
      await lessonsApi.complete(lesson.id)
      setCompleted(true)
      
      // Показываем успех и возвращаемся к курсу
      setTimeout(() => {
        navigate(`/courses/${lesson.course_id}`)
      }, 1500)
    } catch (error) {
      console.error('Ошибка отметки урока:', error)
    }
  }

  if (loading) {
    return <div className="loading">Загрузка...</div>
  }

  if (accessDenied || (lesson && !lesson.is_free && !lesson.course_id)) {
    return (
      <div className="lesson-page">
        <div className="error">
          <h2>🔒 Доступ ограничен</h2>
          <p>Для просмотра этого урока необходимо приобрести курс.</p>
          <button 
            onClick={() => navigate(`/courses/${lesson?.course_id || ''}`)}
            className="btn"
          >
            Перейти к курсу
          </button>
        </div>
      </div>
    )
  }

  if (!lesson) {
    return <div className="error">Урок не найден</div>
  }

  return (
    <div className="lesson-page">
      {/* Заголовок */}
      <div className="lesson-header">
        <button className="back-btn" onClick={() => navigate(-1)}>
          ← Назад
        </button>
        <h1>{lesson.title}</h1>
        {lesson.description && <p>{lesson.description}</p>}
      </div>

      {/* Видео */}
      {lesson.video_url && (
        <div className="lesson-video">
          {/* Если это YouTube - используем iframe */}
          {lesson.video_url.includes('youtube') || lesson.video_url.includes('youtu.be') ? (
            <iframe
              src={getYouTubeEmbedUrl(lesson.video_url)}
              title={lesson.title}
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
              className="video-iframe"
            />
          ) : (
            <video controls src={lesson.video_url} className="video-player">
              Ваш браузер не поддерживает видео.
            </video>
          )}
        </div>
      )}

      {/* PDF и материалы */}
      {lesson.pdf_url && (
        <div className="lesson-materials">
          <h3>📄 Материалы к уроку</h3>
          <a
            href={lesson.pdf_url}
            target="_blank"
            rel="noopener noreferrer"
            className="download-btn"
          >
            Скачать PDF
          </a>
        </div>
      )}

      {/* Кнопка завершения */}
      <div className="lesson-actions">
        {!completed ? (
          <button className="complete-btn" onClick={handleCompleteLesson}>
            ✓ Завершить урок
          </button>
        ) : (
          <div className="completed-message">
            ✅ Урок завершён! Молодец!
          </div>
        )}
      </div>
    </div>
  )
}

export default LessonPage

