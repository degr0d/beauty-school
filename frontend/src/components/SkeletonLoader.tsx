/**
 * Компонент скелетона для загрузки
 */

interface SkeletonLoaderProps {
  type?: 'card' | 'text' | 'title' | 'avatar' | 'list'
  count?: number
  className?: string
}

const SkeletonLoader = ({ type = 'card', count = 1, className = '' }: SkeletonLoaderProps) => {
  if (type === 'card') {
    return (
      <>
        {Array.from({ length: count }).map((_, i) => (
          <div key={i} className={`skeleton skeleton-card ${className}`} style={{
            padding: '20px',
            marginBottom: '20px',
            backgroundColor: '#f9f9f9',
            borderRadius: '12px'
          }}>
            <div className="skeleton skeleton-title" style={{ marginBottom: '15px' }}></div>
            <div className="skeleton skeleton-text" style={{ marginBottom: '10px' }}></div>
            <div className="skeleton skeleton-text short" style={{ marginBottom: '10px' }}></div>
          </div>
        ))}
      </>
    )
  }

  if (type === 'list') {
    return (
      <>
        {Array.from({ length: count }).map((_, i) => (
          <div key={i} className={`skeleton ${className}`} style={{
            height: '60px',
            marginBottom: '15px',
            borderRadius: '8px'
          }}></div>
        ))}
      </>
    )
  }

  if (type === 'text') {
    return (
      <>
        {Array.from({ length: count }).map((_, i) => (
          <div key={i} className={`skeleton skeleton-text ${className}`} style={{
            height: '16px',
            marginBottom: i < count - 1 ? '10px' : '0',
            width: i === count - 1 ? '60%' : '100%'
          }}></div>
        ))}
      </>
    )
  }

  if (type === 'title') {
    return <div className={`skeleton skeleton-title ${className}`} style={{ height: '24px', width: '80%' }}></div>
  }

  if (type === 'avatar') {
    return <div className={`skeleton skeleton-avatar ${className}`} style={{ width: '50px', height: '50px', borderRadius: '50%' }}></div>
  }

  return null
}

export default SkeletonLoader

