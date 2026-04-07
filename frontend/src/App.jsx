import { useLocation, Routes, Route, NavLink } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { AnimatePresence, motion } from 'framer-motion'
import { Scroll, Monitor, Graph, Target, BookOpen, Database } from '@phosphor-icons/react'
import { fetchScores, STATIC_MODE } from './api'

import StoryPage from './pages/StoryPage'
import GlobalOverview from './pages/GlobalOverview'
import TopologyView from './pages/TopologyView'
import CountryDetail from './pages/CountryDetail'
import ScenarioWorkspace from './pages/ScenarioWorkspace'
import MethodologyView from './pages/MethodologyView'

const navItems = [
  { path: '/story', label: 'Story', icon: Scroll },
  { path: '/', label: 'Overview', icon: Monitor },
  { path: '/topology', label: 'Topology', icon: Graph },
  { path: '/scenario', label: 'Scenarios', icon: Target },
  { path: '/methodology', label: 'Methodology', icon: BookOpen },
]

export default function App() {
  const location = useLocation();
  const { data: scoresData } = useQuery({ queryKey: ['scores'], queryFn: fetchScores })
  
  // Calculate max score for the pulse dot
  let maxScore = 0;
  if (scoresData?.scores) {
    const escalations = scoresData.scores.filter(s => s.domain_id === 'escalation_composite');
    escalations.forEach(s => {
      if (s.score > maxScore) maxScore = s.score;
    });
  }

  const pulseColor = maxScore >= 60 ? 'var(--score-red)' : (maxScore >= 30 ? 'var(--score-amber)' : 'var(--score-green)');

  return (
    <div className="min-h-screen flex flex-col bg-[var(--bg-primary)]">
      {/* Navigation */}
      <nav className="flex items-center gap-1 px-6 py-3 border-b" style={{ borderColor: 'var(--border)', background: 'var(--bg-secondary)' }}>
        <div className="flex items-center gap-3 mr-8">
          <div className="w-3 h-3 rounded-full pulse-glow" style={{ backgroundColor: pulseColor,boxShadow: `0 0 8px ${pulseColor}` }}></div>
          <span className="text-lg font-bold tracking-wide" style={{ color: 'var(--text-primary)' }}>GRIP</span>
          <span className="text-xs hidden md:inline" style={{ color: 'var(--text-muted)' }}>Geopolitical Resilience Intelligence Platform</span>
        </div>
        <div className="flex gap-4 ml-auto md:ml-0">
          {navItems.map(item => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/' || item.path === '/story'}
                className={({ isActive }) => `flex items-center gap-2 pb-1 border-b-2 transition-colors ${isActive ? 'border-[var(--text-primary)] text-[var(--text-primary)]' : 'border-transparent text-[var(--text-muted)] hover:text-[var(--text-secondary)]'}`}
              >
                <Icon size={18} weight="bold" />
                <span className="text-sm font-medium">{item.label}</span>
              </NavLink>
            )
          })}
        </div>
      </nav>

      {/* Static Mode Indicator */}
      {STATIC_MODE && (
        <div className="flex items-center justify-center gap-2 px-6 py-1.5 text-xs font-bold uppercase tracking-wider"
             style={{ background: '#0c4a6e', color: '#7dd3fc', borderBottom: '1px solid #0369a1' }}>
          <Database size={14} weight="bold" />
          <span>Portfolio Mode — Pre-computed data snapshot</span>
          <span className="hidden sm:inline" style={{ color: '#38bdf8' }}>·</span>
          <span className="hidden sm:inline" style={{ color: '#38bdf8', fontWeight: 500 }}>Run locally for live analysis</span>
        </div>
      )}

      {/* Routes */}
      <main className="flex-1 p-6 relative overflow-auto">
        <AnimatePresence mode="wait">
          <Routes location={location} key={location.pathname}>
            <Route path="/story" element={
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.4, ease: "easeOut" }}>
                <StoryPage />
              </motion.div>
            } />
            <Route path="/" element={
              <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.25, ease: "easeOut" }}>
                <GlobalOverview />
              </motion.div>
            } />
            <Route path="/topology" element={
              <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.25, ease: "easeOut" }}>
                <TopologyView />
              </motion.div>
            } />
            <Route path="/country/:id" element={
              <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.25, ease: "easeOut" }}>
                <CountryDetail />
              </motion.div>
            } />
            <Route path="/scenario" element={
              <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.25, ease: "easeOut" }}>
                <ScenarioWorkspace />
              </motion.div>
            } />
            <Route path="/methodology" element={
              <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.25, ease: "easeOut" }}>
                <MethodologyView />
              </motion.div>
            } />
          </Routes>
        </AnimatePresence>
      </main>
    </div>
  )
}
