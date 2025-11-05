/**
 * Error Boundary для отлова ошибок React
 */

import { Component, ErrorInfo, ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    }
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('❌ Error Boundary поймал ошибку:', error)
    console.error('📍 Error Info:', errorInfo)
    
    this.setState({
      error,
      errorInfo,
    })
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          padding: '20px',
          maxWidth: '600px',
          margin: '50px auto',
          fontFamily: 'system-ui, -apple-system, sans-serif',
        }}>
          <h1 style={{ color: '#f44336', marginBottom: '16px' }}>
            ⚠️ Произошла ошибка
          </h1>
          <p style={{ marginBottom: '16px', color: '#666' }}>
            К сожалению, приложение не смогло загрузиться. Пожалуйста, проверьте консоль браузера для подробностей.
          </p>
          
          {this.state.error && (
            <details style={{ 
              marginTop: '20px', 
              padding: '12px', 
              backgroundColor: '#f5f5f5', 
              borderRadius: '4px',
              fontSize: '14px',
            }}>
              <summary style={{ cursor: 'pointer', fontWeight: 'bold', marginBottom: '8px' }}>
                Детали ошибки
              </summary>
              <pre style={{ 
                overflow: 'auto', 
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
              }}>
                {this.state.error.toString()}
                {this.state.errorInfo?.componentStack}
              </pre>
            </details>
          )}
          
          <button
            onClick={() => {
              window.location.reload()
            }}
            style={{
              marginTop: '20px',
              padding: '12px 24px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '16px',
            }}
          >
            🔄 Перезагрузить страницу
          </button>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary

