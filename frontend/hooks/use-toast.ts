// Toast hook for notifications
import { useState, useCallback } from 'react'

export interface Toast {
  id: string
  title?: string
  description?: string
  variant?: 'default' | 'destructive'
  duration?: number
}

type ToastInput = Omit<Toast, 'id'>

let toastCount = 0

export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>([])

  const toast = useCallback((input: ToastInput) => {
    const id = (++toastCount).toString()
    const newToast: Toast = {
      id,
      duration: 5000,
      ...input,
    }

    setToasts((prev) => [...prev, newToast])

    // Auto-remove after duration
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id))
    }, newToast.duration)

    return {
      id,
      dismiss: () => setToasts((prev) => prev.filter((t) => t.id !== id)),
      update: (updates: Partial<ToastInput>) => {
        setToasts((prev) =>
          prev.map((t) =>
            t.id === id ? { ...t, ...updates } : t
          )
        )
      },
    }
  }, [])

  const dismiss = useCallback((toastId: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== toastId))
  }, [])

  return {
    toast,
    dismiss,
    toasts,
  }
}

// Simple toast notification queue
let toastQueue: ToastInput[] = []
let toastListeners: Array<(toasts: ToastInput[]) => void> = []

const notifyListeners = () => {
  toastListeners.forEach(listener => listener([...toastQueue]))
}

export const addToast = (input: ToastInput) => {
  toastQueue.push(input)
  notifyListeners()
  
  // Auto-remove after duration
  setTimeout(() => {
    toastQueue = toastQueue.filter(t => t !== input)
    notifyListeners()
  }, input.duration || 5000)
}

export const subscribeToToasts = (listener: (toasts: ToastInput[]) => void) => {
  toastListeners.push(listener)
  return () => {
    toastListeners = toastListeners.filter(l => l !== listener)
  }
}

// Export the toast function for direct use
export const toast = (input: ToastInput) => {
  // For client-side usage, we'll use a simple alert as fallback
  if (typeof window !== 'undefined') {
    const message = input.title ? `${input.title}: ${input.description || ''}` : input.description || ''
    if (input.variant === 'destructive') {
      console.error(message)
    } else {
      console.log(message)
    }
  }
}