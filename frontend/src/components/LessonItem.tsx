/**
 * Компонент элемента урока в списке
 */

import { Link } from 'react-router-dom'

interface LessonItemProps {
  lesson: {
    id: number
    title: string
    order: number
    video_duration?: number
    completed?: boolean
    is_free?: boolean
  }
  courseId?: number // Пока не используется, но может пригодиться в будущем
}

const LessonItem = ({ lesson }: LessonItemProps) => {
  return (
    <Link
      to={`/lessons/${lesson.id}`}
      className={`lesson-item ${lesson.completed ? 'completed' : ''}`}
    >
      <div className="lesson-number">{lesson.order}</div>
      
      <div className="lesson-info">
        <h4 className="lesson-title">{lesson.title}</h4>
        {lesson.video_duration && (
          <span className="lesson-duration">
            ⏱ {formatDuration(lesson.video_duration)}
          </span>
        )}
      </div>

      {lesson.completed && (
        <div className="lesson-checkmark">✓</div>
      )}
    </Link>
  )
}

// Форматирование длительности (секунды -> мм:сс)
function formatDuration(seconds: number): string {
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}

export default LessonItem

