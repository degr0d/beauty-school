/**
 * Компонент рулетки выбора (как в будильнике iPhone)
 */

import { useEffect, useRef, useState, useCallback } from 'react'

interface PickerWheelProps {
  items: string[]
  selectedIndex: number
  onSelect: (index: number) => void
  label?: string
}

const PickerWheel = ({ items, selectedIndex, onSelect, label }: PickerWheelProps) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const [isScrolling, setIsScrolling] = useState(false)
  const itemHeight = 60
  const visibleItems = 5
  const offset = Math.floor(visibleItems / 2) * itemHeight

  const scrollToItem = useCallback((index: number, behavior: ScrollBehavior = 'smooth') => {
    if (containerRef.current) {
      const targetScroll = index * itemHeight
      containerRef.current.scrollTo({
        top: targetScroll,
        behavior: behavior
      })
    }
  }, [itemHeight])

  useEffect(() => {
    if (selectedIndex >= 0 && selectedIndex < items.length) {
      scrollToItem(selectedIndex, 'auto')
    }
  }, [selectedIndex, items.length, scrollToItem])

  const handleScroll = useCallback(() => {
    if (containerRef.current && !isScrolling) {
      setIsScrolling(true)
      clearTimeout((containerRef.current as any).scrollTimeout)
      ;(containerRef.current as any).scrollTimeout = setTimeout(() => {
        const scrollTop = containerRef.current?.scrollTop || 0
        const newIndex = Math.round(scrollTop / itemHeight)
        const clampedIndex = Math.max(0, Math.min(newIndex, items.length - 1))
        if (clampedIndex !== selectedIndex) {
          onSelect(clampedIndex)
          scrollToItem(clampedIndex)
        }
        setIsScrolling(false)
      }, 150)
    }
  }, [itemHeight, isScrolling, onSelect, selectedIndex, items.length, scrollToItem])

  const handleTouchMove = useCallback(() => {
    setIsScrolling(true)
    if (containerRef.current) {
      clearTimeout((containerRef.current as any).scrollTimeout)
    }
  }, [])

  const handleTouchEnd = useCallback(() => {
    if (containerRef.current) {
      clearTimeout((containerRef.current as any).scrollTimeout)
      ;(containerRef.current as any).scrollTimeout = setTimeout(() => {
        const scrollTop = containerRef.current?.scrollTop || 0
        const newIndex = Math.round(scrollTop / itemHeight)
        const clampedIndex = Math.max(0, Math.min(newIndex, items.length - 1))
        if (clampedIndex !== selectedIndex) {
          onSelect(clampedIndex)
          scrollToItem(clampedIndex)
        }
        setIsScrolling(false)
      }, 150)
    }
  }, [itemHeight, onSelect, selectedIndex, items.length, scrollToItem])

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      width: '150px',
      userSelect: 'none',
      WebkitUserSelect: 'none',
      touchAction: 'pan-y'
    }}>
      {label && (
        <div style={{
          fontSize: '14px',
          color: '#888',
          marginBottom: '10px',
          fontWeight: 'bold'
        }}>
          {label}
        </div>
      )}
      <div
        ref={containerRef}
        onScroll={handleScroll}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        style={{
          height: `${visibleItems * itemHeight}px`,
          overflowY: 'scroll',
          overflowX: 'hidden',
          scrollSnapType: 'y mandatory',
          WebkitOverflowScrolling: 'touch',
          position: 'relative',
          width: '100%',
          maskImage: 'linear-gradient(to bottom, transparent, black 20%, black 80%, transparent)',
          WebkitMaskImage: 'linear-gradient(to bottom, transparent, black 20%, black 80%, transparent)',
          scrollbarWidth: 'none',
          msOverflowStyle: 'none'
        }}
        onWheel={(e) => {
          e.preventDefault()
          if (containerRef.current) {
            containerRef.current.scrollTop += e.deltaY
          }
        }}
      >
        <style>{`
          div::-webkit-scrollbar {
            display: none;
          }
        `}</style>
        <div style={{ height: offset }} />
        {items.map((item, index) => (
          <div
            key={index}
            style={{
              height: `${itemHeight}px`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              scrollSnapAlign: 'center',
              fontSize: selectedIndex === index ? '20px' : '16px',
              fontWeight: selectedIndex === index ? 'bold' : 'normal',
              color: selectedIndex === index ? '#e91e63' : '#aaa',
              transition: 'all 0.1s ease-out',
              pointerEvents: 'none'
            }}
          >
            {item}
          </div>
        ))}
        <div style={{ height: offset }} />
      </div>
    </div>
  )
}

export default PickerWheel


