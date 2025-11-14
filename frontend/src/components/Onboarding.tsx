/**
 * Компонент онбординга для новых пользователей
 */

import { useState } from 'react'

interface OnboardingProps {
  onComplete: () => void
}

const Onboarding = ({ onComplete }: OnboardingProps) => {
  const [currentStep, setCurrentStep] = useState(0)

  const steps = [
    {
      title: 'Добро пожаловать в Beauty School! 👋',
      description: 'Онлайн-платформа для обучения бьюти-профессиям',
      icon: '🎓',
      buttonText: 'Далее'
    },
    {
      title: 'Выбирайте курсы 📚',
      description: 'Изучайте маникюр, педикюр, наращивание ресниц и многое другое',
      icon: '💅',
      buttonText: 'Далее'
    },
    {
      title: 'Зарабатывайте баллы 🏆',
      description: 'Получайте баллы за прохождение уроков и достижения',
      icon: '⭐',
      buttonText: 'Далее'
    },
    {
      title: 'Получайте сертификаты 📜',
      description: 'После завершения курса вы получите сертификат',
      icon: '🎉',
      buttonText: 'Начать обучение'
    }
  ]

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1)
    } else {
      // Сохраняем что онбординг пройден
      localStorage.setItem('onboarding_completed', 'true')
      onComplete()
    }
  }

  const handleSkip = () => {
    localStorage.setItem('onboarding_completed', 'true')
    onComplete()
  }

  const currentStepData = steps[currentStep]

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999,
      padding: '20px'
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '20px',
        padding: '40px 30px',
        maxWidth: '400px',
        width: '100%',
        textAlign: 'center',
        boxShadow: '0 10px 40px rgba(0, 0, 0, 0.2)',
        animation: 'fadeIn 0.3s ease-out'
      }}>
        <div style={{ fontSize: '64px', marginBottom: '20px' }}>
          {currentStepData.icon}
        </div>
        <h2 style={{ 
          marginBottom: '15px', 
          fontSize: '24px', 
          fontWeight: 'bold',
          color: '#333'
        }}>
          {currentStepData.title}
        </h2>
        <p style={{ 
          marginBottom: '30px', 
          fontSize: '16px', 
          color: '#666',
          lineHeight: '1.6'
        }}>
          {currentStepData.description}
        </p>
        
        {/* Индикатор шагов */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          gap: '8px',
          marginBottom: '30px'
        }}>
          {steps.map((_, index) => (
            <div
              key={index}
              style={{
                width: index === currentStep ? '24px' : '8px',
                height: '8px',
                borderRadius: '4px',
                backgroundColor: index === currentStep ? '#e91e63' : '#e0e0e0',
                transition: 'all 0.3s ease'
              }}
            />
          ))}
        </div>

        {/* Кнопки */}
        <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
          {currentStep < steps.length - 1 && (
            <button
              onClick={handleSkip}
              style={{
                padding: '12px 24px',
                backgroundColor: 'transparent',
                color: '#666',
                border: '1px solid #e0e0e0',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              Пропустить
            </button>
          )}
          <button
            onClick={handleNext}
            style={{
              padding: '12px 32px',
              backgroundColor: '#e91e63',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: 'bold',
              flex: 1
            }}
          >
            {currentStepData.buttonText}
          </button>
        </div>
      </div>
    </div>
  )
}

export default Onboarding

