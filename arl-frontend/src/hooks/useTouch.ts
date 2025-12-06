import { useEffect, useRef } from 'react'

interface TouchHandlers {
  onSwipeLeft?: () => void
  onSwipeRight?: () => void
  onSwipeUp?: () => void
  onSwipeDown?: () => void
  onLongPress?: () => void
  onDoubleTap?: () => void
}

interface TouchOptions {
  minSwipeDistance?: number
  maxSwipeTime?: number
  longPressDelay?: number
  doubleTapDelay?: number
}

const DEFAULT_OPTIONS: Required<TouchOptions> = {
  minSwipeDistance: 50,
  maxSwipeTime: 300,
  longPressDelay: 500,
  doubleTapDelay: 300,
}

export function useTouch(
  elementRef: React.RefObject<HTMLElement>,
  handlers: TouchHandlers,
  options: TouchOptions = {}
) {
  const opts = { ...DEFAULT_OPTIONS, ...options }
  const touchStart = useRef<{ x: number; y: number; time: number } | null>(null)
  const longPressTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const lastTap = useRef<number>(0)

  useEffect(() => {
    const element = elementRef.current
    if (!element) return

    const handleTouchStart = (e: TouchEvent) => {
      const touch = e.touches[0]
      touchStart.current = {
        x: touch.clientX,
        y: touch.clientY,
        time: Date.now(),
      }

      // Long press detection
      if (handlers.onLongPress) {
        longPressTimer.current = setTimeout(() => {
          handlers.onLongPress?.()
        }, opts.longPressDelay)
      }

      // Double tap detection
      const now = Date.now()
      if (handlers.onDoubleTap && now - lastTap.current < opts.doubleTapDelay) {
        handlers.onDoubleTap()
        lastTap.current = 0
      } else {
        lastTap.current = now
      }
    }

    const handleTouchMove = () => {
      // Cancel long press if user moves finger
      if (longPressTimer.current) {
        clearTimeout(longPressTimer.current)
        longPressTimer.current = null
      }
    }

    const handleTouchEnd = (e: TouchEvent) => {
      if (longPressTimer.current) {
        clearTimeout(longPressTimer.current)
        longPressTimer.current = null
      }

      if (!touchStart.current) return

      const touch = e.changedTouches[0]
      const deltaX = touch.clientX - touchStart.current.x
      const deltaY = touch.clientY - touchStart.current.y
      const deltaTime = Date.now() - touchStart.current.time

      const absDeltaX = Math.abs(deltaX)
      const absDeltaY = Math.abs(deltaY)

      // Horizontal swipe detection
      if (
        absDeltaX > opts.minSwipeDistance &&
        absDeltaX > absDeltaY &&
        deltaTime < opts.maxSwipeTime
      ) {
        if (deltaX > 0 && handlers.onSwipeRight) {
          e.preventDefault()
          handlers.onSwipeRight()
        } else if (deltaX < 0 && handlers.onSwipeLeft) {
          e.preventDefault()
          handlers.onSwipeLeft()
        }
      }

      // Vertical swipe detection
      if (
        absDeltaY > opts.minSwipeDistance &&
        absDeltaY > absDeltaX &&
        deltaTime < opts.maxSwipeTime
      ) {
        if (deltaY > 0 && handlers.onSwipeDown) {
          e.preventDefault()
          handlers.onSwipeDown()
        } else if (deltaY < 0 && handlers.onSwipeUp) {
          e.preventDefault()
          handlers.onSwipeUp()
        }
      }

      touchStart.current = null
    }

    const handleTouchCancel = () => {
      if (longPressTimer.current) {
        clearTimeout(longPressTimer.current)
        longPressTimer.current = null
      }
      touchStart.current = null
    }

    element.addEventListener('touchstart', handleTouchStart, { passive: false })
    element.addEventListener('touchmove', handleTouchMove, { passive: true })
    element.addEventListener('touchend', handleTouchEnd, { passive: false })
    element.addEventListener('touchcancel', handleTouchCancel)

    return () => {
      element.removeEventListener('touchstart', handleTouchStart)
      element.removeEventListener('touchmove', handleTouchMove)
      element.removeEventListener('touchend', handleTouchEnd)
      element.removeEventListener('touchcancel', handleTouchCancel)

      if (longPressTimer.current) {
        clearTimeout(longPressTimer.current)
      }
    }
  }, [elementRef, handlers, opts])
}
