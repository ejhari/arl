import { useEffect, useState } from 'react'

interface LiveRegionProps {
  message: string
  politeness?: 'polite' | 'assertive'
  atomic?: boolean
  clearOnUnmount?: boolean
}

export function LiveRegion({
  message,
  politeness = 'polite',
  atomic = true,
  clearOnUnmount = false,
}: LiveRegionProps) {
  const [announcement, setAnnouncement] = useState('')

  useEffect(() => {
    // Delay to ensure screen reader picks up change
    const timer = setTimeout(() => {
      setAnnouncement(message)
    }, 100)

    return () => {
      clearTimeout(timer)
      if (clearOnUnmount) {
        setAnnouncement('')
      }
    }
  }, [message, clearOnUnmount])

  return (
    <div
      role="status"
      aria-live={politeness}
      aria-atomic={atomic}
      className="sr-only"
    >
      {announcement}
    </div>
  )
}

// Hook for announcing messages to screen readers
export function useLiveAnnouncement() {
  const [message, setMessage] = useState('')

  const announce = (text: string, _politeness: 'polite' | 'assertive' = 'polite') => {
    setMessage('')
    setTimeout(() => setMessage(text), 100)
  }

  return { message, announce }
}
