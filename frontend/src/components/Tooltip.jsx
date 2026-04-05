import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

export default function Tooltip({ children, content, position = 'top' }) {
  const [show, setShow] = useState(false)

  return (
    <div 
      className="relative inline-flex items-center justify-center cursor-help"
      onMouseEnter={() => setShow(true)}
      onMouseLeave={() => setShow(false)}
    >
      {children}
      <AnimatePresence>
        {show && content && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            className={`absolute z-50 px-3 py-2 text-xs font-medium text-[#f1f5f9] bg-[#0f172a] border border-[#334155] rounded shadow-xl pointer-events-none whitespace-nowrap
              ${position === 'top' ? 'bottom-full mb-2' : ''}
              ${position === 'bottom' ? 'top-full mt-2' : ''}
              ${position === 'right' ? 'left-full ml-2' : ''}
              ${position === 'left' ? 'right-full mr-2' : ''}
            `}
          >
            {content}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
