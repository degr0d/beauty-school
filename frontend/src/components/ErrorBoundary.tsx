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
    console.error('📍 Stack trace:', error.stack)
    console.error('📍 Component stack:', errorInfo.componentStack)
    
    // Пытаемся показать ошибку на экране
    try {
      const errorDiv = document.createElement('div')
      errorDiv.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; background: #dc3545; color: white; padding: 20px; z-index: 99999; font-family: monospace; font-size: 12px; max-height: 50vh; overflow: auto;'
      errorDiv.innerHTML = `
        <h3 style="margin: 0 0 10px 0;">❌ React Error #301</h3>
        <p style="margin: 0 0 10px 0;"><strong>Ошибка:</strong> ${error.message}</p>
        <details style="margin-top: 10px;">
          <summary style="cursor: pointer; font-weight: bold;">Stack trace</summary>
          <pre style="background: rgba(0,0,0,0.3); padding: 10px; margin: 10px 0; overflow: auto; white-space: pre-wrap;">${error.stack || 'Нет stack trace'}</pre>
        </details>
        <details style="margin-top: 10px;">
          <summary style="cursor: pointer; font-weight: bold;">Component stack</summary>
          <pre style="background: rgba(0,0,0,0.3); padding: 10px; margin: 10px 0; overflow: auto; white-space: pre-wrap;">${errorInfo.componentStack || 'Нет component stack'}</pre>
        </details>
        <button onclick="this.parentElement.remove()" style="margin-top: 10px; padding: 8px 16px; background: white; color: #dc3545; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">Закрыть</button>
      `
      document.body.appendChild(errorDiv)
    } catch (e) {
      console.error('Не удалось показать ошибку на экране:', e)
    }
    
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

