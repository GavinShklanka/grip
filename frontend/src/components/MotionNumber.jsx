import { useEffect } from 'react'
import { motion, useSpring, useTransform } from 'framer-motion'

export default function MotionNumber({ value, decimals = 1, className = "" }) {
  const spring = useSpring(0, { stiffness: 50, damping: 20 })
  
  useEffect(() => {
    spring.set(value)
  }, [value, spring])

  const display = useTransform(spring, v => v.toFixed(decimals))

  return <motion.span className={className}>{display}</motion.span>
}
