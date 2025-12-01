import { useEffect } from 'react'

export interface KeyboardNavOptions {
  onPrevious?: () => void
  onNext?: () => void
  onSelect?: () => void
  onEscape?: () => void
  onSearch?: () => void
  onEdit?: () => void
  onPin?: () => void
  enabled?: boolean
}

export function useKeyboardNav(options: KeyboardNavOptions) {
  const { enabled = true } = options

  useEffect(() => {
    if (!enabled) return

    const handleKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement
      const isInput = ['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName)
      const isContentEditable = target.isContentEditable

      // Skip if typing in input/textarea or content editable
      if (isInput || isContentEditable) {
        // Only allow Escape key in inputs
        if (e.key === 'Escape' && options.onEscape) {
          e.preventDefault()
          options.onEscape()
        }
        return
      }

      switch (e.key) {
        // Navigation keys
        case 'j':
        case 'ArrowDown':
          e.preventDefault()
          options.onNext?.()
          break

        case 'k':
        case 'ArrowUp':
          e.preventDefault()
          options.onPrevious?.()
          break

        // Selection keys
        case 'Enter':
          if (!e.shiftKey && !e.ctrlKey && !e.metaKey) {
            e.preventDefault()
            options.onSelect?.()
          }
          break

        case ' ':
          // Space key (scroll if no action)
          if (options.onSelect) {
            e.preventDefault()
            options.onSelect()
          }
          break

        // Modal/dialog keys
        case 'Escape':
          e.preventDefault()
          options.onEscape?.()
          break

        // Action keys
        case '/':
          e.preventDefault()
          options.onSearch?.()
          break

        case 'e':
          if (!e.ctrlKey && !e.metaKey) {
            e.preventDefault()
            options.onEdit?.()
          }
          break

        case 'p':
          if (!e.ctrlKey && !e.metaKey) {
            e.preventDefault()
            options.onPin?.()
          }
          break
      }

      // Cmd/Ctrl + K for command palette
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        options.onSearch?.()
      }

      // Cmd/Ctrl + E for edit
      if ((e.metaKey || e.ctrlKey) && e.key === 'e') {
        e.preventDefault()
        options.onEdit?.()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [options, enabled])
}

export function useKeyboardShortcut(
  key: string,
  callback: () => void,
  options: {
    ctrl?: boolean
    meta?: boolean
    shift?: boolean
    alt?: boolean
    enabled?: boolean
  } = {}
) {
  const { enabled = true, ctrl = false, meta = false, shift = false, alt = false } = options

  useEffect(() => {
    if (!enabled) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if (
        e.key.toLowerCase() === key.toLowerCase() &&
        e.ctrlKey === ctrl &&
        e.metaKey === meta &&
        e.shiftKey === shift &&
        e.altKey === alt
      ) {
        e.preventDefault()
        callback()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [key, callback, ctrl, meta, shift, alt, enabled])
}
