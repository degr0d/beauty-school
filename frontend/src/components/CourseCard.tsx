/**
 * Компонент карточки курса
 */

import { Link } from 'react-router-dom'
import type { Course } from '../api/client'

interface CourseCardProps {
  course: Course
}

const CourseCard = ({ course }: CourseCardProps) => {
  return (
    <Link to={`/courses/${course.id}`} className="course-card">
      {/* Обложка курса */}
      {course.cover_image_url && (
        <div className="course-cover">
          <img src={course.cover_image_url} alt={course.title} />
        </div>
      )}

      {/* Информация о курсе */}
      <div className="course-info">
        {course.is_top && <span className="badge-top">🔥 Топ</span>}
        
        <h3 className="course-title">{course.title}</h3>
        <p className="course-description">{course.description}</p>
        
        <div className="course-meta">
          <span className="category">{getCategoryLabel(course.category)}</span>
          {course.duration_hours && (
            <span className="duration">⏱ {course.duration_hours} ч</span>
          )}
        </div>

        {course.price > 0 && (
          <div className="course-price">{course.price} ₽</div>
        )}
      </div>
    </Link>
  )
}

// Маппинг категорий на русские названия
function getCategoryLabel(category: string): string {
  const labels: Record<string, string> = {
    manicure: 'Маникюр',
    pedicure: 'Педикюр',
    eyelashes: 'Ресницы',
    eyebrows: 'Брови',
    podology: 'Подология',
    marketing: 'Маркетинг',
    business: 'Своё дело',
  }
  return labels[category] || category
}

export default CourseCard

