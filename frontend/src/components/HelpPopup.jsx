import { useState, useEffect, useRef } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faTimes } from '@fortawesome/free-solid-svg-icons'

export default function HelpPopup({ children, content, title = "Information" }) {
  const [isOpen, setIsOpen] = useState(false)
  const popupRef = useRef(null)
  const triggerRef = useRef(null)

  useEffect(() => {
    function handleClickOutside(event) {
      if (popupRef.current && !popupRef.current.contains(event.target) && 
          triggerRef.current && !triggerRef.current.contains(event.target)) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
      document.addEventListener('touchstart', handleClickOutside)
      return () => {
        document.removeEventListener('mousedown', handleClickOutside)
        document.removeEventListener('touchstart', handleClickOutside)
      }
    }
  }, [isOpen])

  useEffect(() => {
    function handleEscape(event) {
      if (event.key === 'Escape') {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEscape)
      return () => document.removeEventListener('keydown', handleEscape)
    }
  }, [isOpen])

  return (
    <>
      <button
        ref={triggerRef}
        className="help-popup-trigger"
        onClick={() => setIsOpen(true)}
        type="button"
        aria-label="Show help information"
      >
        {children}
      </button>
      
      {isOpen && (
        <div className="help-popup-overlay">
          <div 
            ref={popupRef}
            className="help-popup-content"
            role="dialog"
            aria-modal="true"
            aria-labelledby="popup-title"
          >
            <div className="help-popup-header">
              <h3 id="popup-title" className="help-popup-title">{title}</h3>
              <button
                onClick={() => setIsOpen(false)}
                className="help-popup-close"
                aria-label="Close popup"
              >
                <FontAwesomeIcon icon={faTimes} />
              </button>
            </div>
            <div className="help-popup-body">
              {content}
            </div>
          </div>
        </div>
      )}
    </>
  )
}