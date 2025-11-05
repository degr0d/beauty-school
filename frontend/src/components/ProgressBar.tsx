/**
 * Компонент прогресс-бара
 */

interface ProgressBarProps {
  percent: number
  showLabel?: boolean
}

const ProgressBar = ({ percent, showLabel = true }: ProgressBarProps) => {
  return (
    <div className="progress-bar-container">
      <div className="progress-bar">
        <div
          className="progress-fill"
          style={{ width: `${Math.min(percent, 100)}%` }}
        />
      </div>
      {showLabel && (
        <span className="progress-label">{Math.round(percent)}%</span>
      )}
    </div>
  )
}

export default ProgressBar

