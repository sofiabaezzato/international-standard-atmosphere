import { useState } from 'react'

export default function HelpTooltip({ children, content, position = 'top' }) {
  const [isVisible, setIsVisible] = useState(false)

  return (
    <div className="tooltip-container">
      <span 
        className="tooltip-trigger"
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
        onClick={() => setIsVisible(!isVisible)}
      >
        {children}
      </span>
      {isVisible && (
        <div className={`tooltip-content tooltip-${position}`}>
          {content}
          <div className="tooltip-arrow"></div>
        </div>
      )}
    </div>
  )
}