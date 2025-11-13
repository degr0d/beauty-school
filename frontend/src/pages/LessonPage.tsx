/**
 * Страница урока (видео + материалы)
 */

import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { lessonsApi, accessApi, coursesApi, type LessonDetail } from '../api/client'

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
  const [nextLessonId, setNextLessonId] = useState<number | null>(null)
  const [courseCompleted, setCourseCompleted] = useState(false)

  useEffect(() => {
    if (id) {
      // Сбрасываем состояние при переходе на новый урок
      setCompleted(false)
      setNextLessonId(null)
      setCourseCompleted(false)
      loadLesson(parseInt(id))
    }
  }, [id])

  const loadLesson = async (lessonId: number) => {
    try {
      const response = await lessonsApi.getById(lessonId)
      const rawLesson = response.data
      
      // Нормализуем урок - гарантируем что все поля это примитивы
      if (rawLesson) {
        const normalizedLesson: LessonDetail = {
          id: typeof rawLesson.id === 'number' && !isNaN(rawLesson.id) ? rawLesson.id : 0,
          title: typeof rawLesson.title === 'string' ? rawLesson.title : 'Без названия',
          order: typeof rawLesson.order === 'number' && !isNaN(rawLesson.order) ? rawLesson.order : 0,
          video_duration: typeof rawLesson.video_duration === 'number' && !isNaN(rawLesson.video_duration) && rawLesson.video_duration > 0 ? rawLesson.video_duration : undefined,
          is_free: rawLesson.is_free === true,
          course_id: typeof rawLesson.course_id === 'number' && !isNaN(rawLesson.course_id) ? rawLesson.course_id : 0,
          description: typeof rawLesson.description === 'string' ? rawLesson.description : undefined,
          video_url: typeof rawLesson.video_url === 'string' && rawLesson.video_url.trim() !== '' ? rawLesson.video_url : undefined,
          pdf_url: typeof rawLesson.pdf_url === 'string' && rawLesson.pdf_url.trim() !== '' ? rawLesson.pdf_url : undefined
        }
        setLesson(normalizedLesson)
        
        // Проверяем доступ к курсу (если урок платный)
        if (!normalizedLesson.is_free && normalizedLesson.course_id) {
          try {
            const accessResponse = await accessApi.checkCourseAccess(normalizedLesson.course_id)
            if (!accessResponse.data.has_access) {
              setAccessDenied(true)
            }
          } catch (error) {
            console.error('Ошибка проверки доступа:', error)
            setAccessDenied(true)
          }
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
      const response = await lessonsApi.complete(lesson.id)
      setCompleted(true)
      
      // Если курс завершен - показываем уведомление
      if (response.data?.course_completed) {
        setCourseCompleted(true)
        alert('🎉 Поздравляем! Вы завершили курс!\n\n✅ Начислено 100 баллов за завершение курса')
        // Отправляем событие для обновления сертификатов в профиле
        window.dispatchEvent(new CustomEvent('course_completed'))
        return
      }
      
      // Если курс не завершен - ищем следующий урок
      alert('✅ Урок завершен!\n\n+10 баллов за завершение урока')
      
      // Загружаем информацию о курсе, чтобы найти следующий урок
      try {
        const courseResponse = await coursesApi.getById(lesson.course_id)
        const course = courseResponse.data
        
        if (course && course.lessons && Array.isArray(course.lessons)) {
          // Сортируем уроки по порядку (order)
          const sortedLessons = [...course.lessons].sort((a: any, b: any) => {
            const orderA = typeof a.order === 'number' ? a.order : 0
            const orderB = typeof b.order === 'number' ? b.order : 0
            return orderA - orderB
          })
          
          // Находим текущий урок в отсортированном списке
          const currentLessonIndex = sortedLessons.findIndex((l: any) => l.id === lesson.id)
          
          console.log('🔍 Поиск следующего урока:', {
            currentLessonId: lesson.id,
            currentLessonIndex,
            totalLessons: sortedLessons.length,
            sortedLessons: sortedLessons.map((l: any) => ({ id: l.id, order: l.order, title: l.title }))
          })
          
          // Ищем следующий урок (после текущего)
          if (currentLessonIndex >= 0 && currentLessonIndex < sortedLessons.length - 1) {
            const nextLesson = sortedLessons[currentLessonIndex + 1]
            if (nextLesson && nextLesson.id) {
              console.log('✅ Следующий урок найден:', { id: nextLesson.id, title: nextLesson.title })
              setNextLessonId(nextLesson.id)
              return
            }
          } else {
            console.log('ℹ️ Следующий урок не найден (это последний урок в курсе)')
          }
        }
      } catch (error) {
        console.error('Ошибка загрузки курса для поиска следующего урока:', error)
      }
      
      // Если следующий урок не найден - не устанавливаем nextLessonId
      // Кнопка "Вернуться к курсу" появится автоматически
    } catch (error) {
      console.error('Ошибка отметки урока:', error)
      alert('Ошибка при завершении урока')
    }
  }

  const handleNextLesson = () => {
    if (nextLessonId) {
      console.log('➡️ Переход к следующему уроку:', nextLessonId)
      navigate(`/lessons/${nextLessonId}`)
    } else {
      console.warn('⚠️ nextLessonId не установлен, переход невозможен')
      // Если nextLessonId не установлен, возвращаемся к курсу
      if (lesson?.course_id) {
        navigate(`/courses/${lesson.course_id}`)
      }
    }
  }

  const handleBackToCourse = () => {
    if (lesson?.course_id) {
      navigate(`/courses/${lesson.course_id}`)
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
          <div className="completed-section">
            <div className="completed-message">
              ✅ Урок завершён! Молодец!
            </div>
            {courseCompleted ? (
              <button className="next-lesson-btn" onClick={handleBackToCourse}>
                🎉 Вернуться к курсу
              </button>
            ) : nextLessonId ? (
              <button className="next-lesson-btn" onClick={handleNextLesson}>
                ➡️ Следующий урок
              </button>
            ) : (
              <button className="next-lesson-btn" onClick={handleBackToCourse}>
                ← Вернуться к курсу
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default LessonPage

