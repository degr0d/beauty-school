/**
 * Компонент прогресс-бара
 */

interface ProgressBarProps {
  percent: number
  showLabel?: boolean
}

const ProgressBar = ({ percent, showLabel = true }: ProgressBarProps) => {
  // Безопасно обрабатываем percent - гарантируем что это число
  const safePercent = typeof percent === 'number' && !isNaN(percent) ? Math.min(Math.max(percent, 0), 100) : 0
  
  return (
    <div className="progress-bar-container">
      <div className="progress-bar">
        <div
          className="progress-fill"
          style={{ width: `${safePercent}%` }}
        />
      </div>
      {showLabel && (
        <span className="progress-label">{Math.round(safePercent)}%</span>
      )}
    </div>
  )
}

export default ProgressBar

