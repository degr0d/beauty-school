/**
 * Компонент рулетки выбора (как в будильнике iPhone)
 */

import { useEffect, useRef, useState } from 'react'

interface PickerWheelProps {
  items: string[]
  selectedIndex: number
  onSelect: (index: number) => void
  label?: string
}

const PickerWheel = ({ items, selectedIndex, onSelect, label }: PickerWheelProps) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [startY, setStartY] = useState(0)
  const [scrollOffset, setScrollOffset] = useState(0)

  useEffect(() => {
    // Прокручиваем к выбранному элементу при загрузке
    if (containerRef.current && selectedIndex >= 0 && selectedIndex < items.length) {
      const itemHeight = 60
      const centerOffset = containerRef.current.clientHeight / 2 - itemHeight / 2
      const targetScroll = selectedIndex * itemHeight - centerOffset
      containerRef.current.scrollTop = targetScroll
      setScrollOffset(targetScroll)
    }
  }, [selectedIndex, items.length])

  const handleScroll = () => {
    if (!containerRef.current || isDragging) return
    
    const itemHeight = 60
    const centerOffset = containerRef.current.clientHeight / 2 - itemHeight / 2
    const scrollTop = containerRef.current.scrollTop
    const newIndex = Math.round((scrollTop + centerOffset) / itemHeight)
    
    if (newIndex >= 0 && newIndex < items.length && newIndex !== selectedIndex) {
      onSelect(newIndex)
    }
    
    setScrollOffset(scrollTop)
  }

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true)
    setStartY(e.clientY)
  }

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging || !containerRef.current) return
    
    const deltaY = e.clientY - startY
    const newScroll = scrollOffset - deltaY
    containerRef.current.scrollTop = newScroll
    setScrollOffset(newScroll)
  }

  const handleMouseUp = () => {
    setIsDragging(false)
    // Снаппинг к ближайшему элементу
    if (containerRef.current) {
      const itemHeight = 60
      const centerOffset = containerRef.current.clientHeight / 2 - itemHeight / 2
      const scrollTop = containerRef.current.scrollTop
      const newIndex = Math.round((scrollTop + centerOffset) / itemHeight)
      const clampedIndex = Math.max(0, Math.min(newIndex, items.length - 1))
      const targetScroll = clampedIndex * itemHeight - centerOffset
      
      containerRef.current.scrollTo({
        top: targetScroll,
        behavior: 'smooth'
      })
      
      if (clampedIndex !== selectedIndex) {
        onSelect(clampedIndex)
      }
    }
  }

  const handleTouchStart = (e: React.TouchEvent) => {
    setIsDragging(true)
    setStartY(e.touches[0].clientY)
  }

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!isDragging || !containerRef.current) return
    
    const deltaY = e.touches[0].clientY - startY
    const newScroll = scrollOffset - deltaY
    containerRef.current.scrollTop = newScroll
    setScrollOffset(newScroll)
  }

  const handleTouchEnd = () => {
    handleMouseUp()
  }

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      {label && (
        <div style={{ 
          marginBottom: '10px', 
          fontSize: '14px', 
          fontWeight: 'bold', 
          color: '#666',
          textAlign: 'center'
        }}>
          {label}
        </div>
      )}
      <div
        ref={containerRef}
        onScroll={handleScroll}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        style={{
          width: '100%',
          height: '200px',
          overflow: 'hidden',
          position: 'relative',
          cursor: isDragging ? 'grabbing' : 'grab',
          userSelect: 'none',
          WebkitUserSelect: 'none'
        }}
      >
        {/* Верхний градиент */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '70px',
          background: 'linear-gradient(to bottom, rgba(255,255,255,1), rgba(255,255,255,0))',
          pointerEvents: 'none',
          zIndex: 2
        }} />
        
        {/* Выделенная область */}
        <div style={{
          position: 'absolute',
          top: '50%',
          left: 0,
          right: 0,
          transform: 'translateY(-50%)',
          height: '60px',
          borderTop: '1px solid #e0e0e0',
          borderBottom: '1px solid #e0e0e0',
          backgroundColor: 'rgba(233, 30, 99, 0.05)',
          pointerEvents: 'none',
          zIndex: 1
        }} />
        
        {/* Нижний градиент */}
        <div style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: '70px',
          background: 'linear-gradient(to top, rgba(255,255,255,1), rgba(255,255,255,0))',
          pointerEvents: 'none',
          zIndex: 2
        }} />
        
        {/* Список элементов */}
        <div style={{
          paddingTop: '70px',
          paddingBottom: '70px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center'
        }}>
          {items.map((item, index) => (
            <div
              key={index}
              style={{
                height: '60px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: index === selectedIndex ? '20px' : '16px',
                fontWeight: index === selectedIndex ? 'bold' : 'normal',
                color: index === selectedIndex ? '#e91e63' : '#666',
                transition: 'all 0.2s ease',
                opacity: Math.abs(index - selectedIndex) > 2 ? 0.3 : 1,
                transform: `scale(${index === selectedIndex ? 1.1 : 1})`
              }}
            >
              {item}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default PickerWheel

