import { useQuery } from '@tanstack/react-query'
import { fetchTopology, fetchOutages } from '../api'
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Atom, Fire, Database, Factory, Info, NavigationArrow } from '@phosphor-icons/react'
import MotionNumber from '../components/MotionNumber'

// Geographically relative positioning mapping (roughly Baltic Sea bounds)
const NODE_POSITIONS = {
  FI: { x: 450, y: 150, label: 'Finland', flag: '🇫🇮' },
  EE: { x: 450, y: 320, label: 'Estonia', flag: '🇪🇪' },
  LV: { x: 400, y: 480, label: 'Latvia', flag: '🇱🇻' },
  LT: { x: 350, y: 640, label: 'Lithuania', flag: '🇱🇹' },
  SE: { x: 150, y: 350, label: 'Sweden', flag: '🇸🇪', context: true },
  PL: { x: 250, y: 750, label: 'Poland', flag: '🇵🇱', context: true },
}

const EDGE_DEFS = [
  { id: 'estlink_1', from: 'FI', to: 'EE', cap: 358, type: 'electric', sub: true, curve: -40 },
  { id: 'estlink_2', from: 'FI', to: 'EE', cap: 650, type: 'electric', sub: true, curve: 40 },
  { id: 'ee_lv_electric', from: 'EE', to: 'LV', cap: 1500, type: 'electric', sub: false, curve: 10 },
  { id: 'lv_lt_electric', from: 'LV', to: 'LT', cap: 1500, type: 'electric', sub: false, curve: -15 },
  { id: 'nordbalt', from: 'SE', to: 'LT', cap: 700, type: 'electric', sub: true, curve: 80 },
  { id: 'litpol_link', from: 'PL', to: 'LT', cap: 500, type: 'electric', sub: false, curve: -20 },
  { id: 'balticconnector', from: 'FI', to: 'EE', cap: 7.2, type: 'gas', sub: true, curve: 90 },
  { id: 'kiemenai', from: 'LV', to: 'LT', cap: 6.0, type: 'gas', sub: false, curve: 20 },
  { id: 'gipl', from: 'PL', to: 'LT', cap: 2.4, type: 'gas', sub: false, curve: 10 },
]

const PLANNED = [
  { id: 'harmony_link', from: 'PL', to: 'LT', cap: 700, label: 'Harmony Link (~2028)', curve: 60, sub: true },
  { id: 'estlink_3', from: 'FI', to: 'EE', cap: 700, label: 'Estlink 3 (~2035)', curve: 140, sub: true },
]

const FACILITIES = [
  { id: 'olkiluoto', country: 'FI', x: 300, y: 130, label: 'Olkiluoto 3 (1650 MW)', type: 'nuclear', icon: Atom },
  { id: 'klaipeda_lng', country: 'LT', x: 280, y: 580, label: 'Klaipėda LNG', type: 'lng', icon: Fire },
  { id: 'inkoo_fsru', country: 'FI', x: 500, y: 140, label: 'Inkoo FSRU', type: 'lng', icon: Fire },
  { id: 'incukalns', country: 'LV', x: 520, y: 460, label: 'Inčukalns UGS', type: 'storage', icon: Database },
  { id: 'narva', country: 'EE', x: 580, y: 310, label: 'Narva (1400 MW)', type: 'thermal', icon: Factory },
]

function getStatusColor(status) {
  if (status === 'offline') return 'var(--score-red)'
  if (status === 'degraded') return 'var(--score-amber)'
  return 'var(--score-green)'
}

function getMarginClass(status) {
  if (status === 'offline') return 'dot-red'
  if (status === 'degraded') return 'dot-amber'
  return 'dot-green'
}

function getStrokeWidth(cap, type) {
  if (type === 'gas') return 4
  return Math.max(3, Math.min(12, cap / 100))
}

export default function TopologyView() {
  const { data: topoData, isLoading } = useQuery({ queryKey: ['topology'], queryFn: fetchTopology })
  const { data: outageData } = useQuery({ queryKey: ['outages'], queryFn: fetchOutages })
  const [activeEdge, setActiveEdge] = useState(null)

  const outages = outageData?.outages ?? []
  const outageMap = {}
  outages.forEach(o => { outageMap[o.edge_id] = o })

  function getEdgeStatus(id) {
    if (outageMap[id]) return outageMap[id].status
    return 'active'
  }

  // Spline generator
  function describeArc(x1, y1, x2, y2, curveDistance) {
    const cx = (x1 + x2) / 2
    const cy = (y1 + y2) / 2
    const angle = Math.atan2(y2 - y1, x2 - x1)
    
    // Calculate control point shifted perpendicular to the line
    const px = cx - Math.sin(angle) * curveDistance
    const py = cy + Math.cos(angle) * curveDistance
    
    return `M ${x1} ${y1} Q ${px} ${py} ${x2} ${y2}`
  }

  return (
    <div className="max-w-7xl mx-auto px-4 pb-12">
      <style>{`
        @keyframes stroke-flow {
          from { stroke-dashoffset: 40; }
          to { stroke-dashoffset: 0; }
        }
        .animate-flow { animation: stroke-flow 1s linear infinite; }
      `}</style>
      <h1 className="text-3xl font-bold tracking-tight mb-2" style={{ color: 'var(--text-primary)' }}>
        Infrastructure Topology
      </h1>
      <p className="text-base mb-6" style={{ color: 'var(--text-secondary)' }}>
        Baltic-Nordic architectural chain. Click links to inspect cross-border telemetry.
      </p>

      {isLoading ? (
        <div className="flex items-center justify-center py-32">
          <div className="w-8 h-8 rounded-full border-4 border-t-transparent animate-spin" style={{ borderColor: 'var(--score-blue)', borderTopColor: 'transparent' }}></div>
        </div>
      ) : (
        <div className="card relative grid grid-cols-1 lg:grid-cols-4 gap-0 p-0 overflow-hidden border border-[var(--border-card)]" style={{ background: 'var(--bg-primary)' }}>
          
          {/* Main SVG Map Area */}
          <div className="lg:col-span-3 min-h-[650px] relative bg-[#0a1628]" style={{ backgroundImage: 'radial-gradient(circle at center, #0a1628 0%, #060d1a 100%)' }}>
            {/* Faint latitude/longitude grid lines */}
            <div className="absolute inset-0 z-0 pointer-events-none" style={{ backgroundImage: 'linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)', backgroundSize: '50px 50px' }}></div>
            
            <svg viewBox="0 0 800 800" className="w-[100%] h-[100%] relative z-10">
              <defs>
                <filter id="glow-active">
                  <feGaussianBlur stdDeviation="4" result="blur" />
                  <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
                </filter>
                <filter id="glow-offline">
                  <feGaussianBlur stdDeviation="6" result="blur" />
                  <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
                </filter>
              </defs>

              {/* Background Baltic Outline Abstraction */}
              <path d="M200,800 Q150,500 300,100 T500,0 T700,100 T800,400 T600,700 Z" fill="#0b1b36" opacity="0.3" />
              <path d="M100,600 Q250,550 400,200 T600,100" fill="none" stroke="#1e293b" strokeWidth="40" strokeLinecap="round" opacity="0.2"/>

              {/* Planned Edges */}
              {PLANNED.map(e => {
                const a = NODE_POSITIONS[e.from]
                const b = NODE_POSITIONS[e.to]
                const path = describeArc(a.x, a.y, b.x, b.y, e.curve)
                return (
                  <g key={e.id}>
                    <path d={path} fill="none" stroke="var(--text-secondary)" strokeWidth={3} strokeDasharray="8 6" opacity={0.3} />
                    <text x={(a.x + b.x) / 2} y={(a.y + b.y) / 2 - 20} fill="var(--text-secondary)" fontSize="10">{e.label}</text>
                  </g>
                )
              })}

              {/* Active Edges */}
              {EDGE_DEFS.map(e => {
                const status = getEdgeStatus(e.id)
                const color = getStatusColor(status)
                const sw = getStrokeWidth(e.cap, e.type)
                const a = NODE_POSITIONS[e.from]
                const b = NODE_POSITIONS[e.to]
                const path = describeArc(a.x, a.y, b.x, b.y, e.curve)
                
                // Dash config: '10 10' for active, solid for offline
                const dashArray = status === 'active' ? (e.type === 'gas' ? '12 8' : '15 15') : 'none'
                const isHovered = activeEdge?.id === e.id
                const isSelected = activeEdge?.id === e.id

                return (
                  <g key={e.id}
                    onClick={() => setActiveEdge({ ...e, status })}
                    onMouseEnter={(ev) => { ev.currentTarget.style.filter = 'brightness(1.5)' }}
                    onMouseLeave={(ev) => { ev.currentTarget.style.filter = 'none' }}
                    style={{ cursor: 'pointer', transition: 'all 0.2s' }}
                  >
                    {/* Invisible Hitbox */}
                    <path d={path} fill="none" stroke="transparent" strokeWidth={24} />
                    {/* Outline / Glow if selected */}
                    {isSelected && <path d={path} fill="none" stroke="white" strokeWidth={sw + 4} opacity={0.3} />}
                    {/* Actual structural line */}
                    <path d={path} fill="none" stroke={color} strokeWidth={sw} opacity={isSelected ? 1.0 : 0.8}
                      strokeDasharray={dashArray}
                      filter={status === 'offline' ? 'url(#glow-offline)' : 'url(#glow-active)'} 
                      className={status === 'active' ? 'animate-flow' : (status === 'offline' ? 'animate-pulse' : '')}
                    />
                  </g>
                )
              })}

              {/* Country Nodes */}
              {Object.entries(NODE_POSITIONS).map(([id, node]) => (
                <g key={id}>
                  {/* Subtle ring glow for active nodes */}
                  {!node.context && (
                    <circle cx={node.x} cy={node.y} r={45}
                      fill="none" stroke="var(--score-green)" strokeWidth={1} opacity={0.2} filter="url(#glow-active)" />
                  )}
                  <circle cx={node.x} cy={node.y} r={node.context ? 25 : 35}
                    fill="var(--bg-card)"
                    stroke={node.context ? '#334155' : 'var(--text-secondary)'} strokeWidth={node.context ? 1 : 2} />
                  <text x={node.x} y={node.y + 4} textAnchor="middle" fill="white" fontSize={node.context ? 18 : 22} style={{ pointerEvents: 'none' }}>
                    {id}
                  </text>
                  <text x={node.x} y={node.y + (node.context ? 40 : 55)} textAnchor="middle"
                    fill={node.context ? 'var(--text-secondary)' : 'var(--text-primary)'} 
                    fontSize={node.context ? 12 : 14} fontWeight={node.context ? 500 : 700}>
                    {node.label}
                  </text>
                </g>
              ))}

              {/* Facilities */}
              {FACILITIES.map(f => {
                const Icon = f.icon;
                return (
                  <g key={f.id} className="cursor-help transition-all duration-300" onMouseEnter={e => e.currentTarget.style.transform = 'scale(1.1)'} onMouseLeave={e => e.currentTarget.style.transform = 'scale(1)'} style={{ transformOrigin: `${f.x}px ${f.y}px` }}>
                    <circle cx={f.x} cy={f.y} r={16} fill="var(--bg-secondary)" stroke="var(--border-card)" strokeWidth="1" filter="drop-shadow(0 4px 6px rgba(0,0,0,0.5))" />
                    {/* Render Phosphor Icon directly into SVG using foreignObject or just pure SVG. Phosphor returns SVG paths, but easiest approach is x/y */}
                    <svg x={f.x - 10} y={f.y - 10} width={20} height={20} fill="var(--text-primary)">
                      <Icon weight="duotone" />
                    </svg>
                    <g className="opacity-0 hover:opacity-100 transition-opacity">
                      <rect x={f.x - 60} y={f.y + 20} width={120} height={24} rx={4} fill="var(--bg-primary)" stroke="var(--border-card)" />
                      <text x={f.x} y={f.y + 36} fill="var(--text-primary)" fontSize="10" textAnchor="middle" fontWeight="bold">{f.label}</text>
                    </g>
                  </g>
                )
              })}
            </svg>
          </div>

          {/* Interactive Inspection Panel */}
          <div className="lg:col-span-1 border-l border-[var(--border-card)] bg-[var(--bg-card)] relative z-20">
            <h3 className="text-sm uppercase tracking-wider font-bold mb-0 p-6 border-b border-[var(--border-card)]" style={{ color: 'var(--text-secondary)' }}>
              Telemetry Inspector
            </h3>
            
            <div className="p-6">
              <AnimatePresence mode="wait">
                {activeEdge ? (
                  <motion.div 
                    key={activeEdge.id}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.15 }}
                    className="flex flex-col gap-5"
                  >
                    <div className="p-5 rounded-lg border border-[var(--border-card)] bg-[#0f172a]" style={{ boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.2)' }}>
                      <div className="flex items-center gap-2 text-xs uppercase tracking-wider mb-2" style={{ color: 'var(--text-secondary)' }}>
                        <NavigationArrow size={14} weight="bold" />
                        {activeEdge.type} • {activeEdge.sub ? 'Submarine' : 'Overland'}
                      </div>
                      <h4 className="text-2xl font-bold font-mono tracking-tight" style={{ color: 'var(--text-primary)' }}>
                        {activeEdge.id.replace(/_/g, ' ').toUpperCase()}
                      </h4>
                    </div>

                    <div className="flex items-center justify-between p-4 rounded-lg bg-[var(--bg-primary)] border border-[var(--border-card)]">
                      <span className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>Structural Status</span>
                      <div className="flex items-center gap-2">
                        <span className={`dot ${getMarginClass(activeEdge.status)} pulse-glow`}></span>
                        <span className="font-mono text-sm uppercase font-bold" style={{ color: getStatusColor(activeEdge.status) }}>
                          {activeEdge.status}
                        </span>
                      </div>
                    </div>

                    <div className="flex flex-col gap-3 p-4 rounded-lg bg-[var(--bg-primary)] border border-[var(--border-card)]">
                      <div className="flex justify-between text-sm items-center">
                        <span style={{ color: 'var(--text-secondary)' }}>Nominal Capacity</span>
                        <span className="font-mono text-lg font-bold" style={{ color: 'var(--text-primary)' }}>
                          <MotionNumber value={activeEdge.cap} decimals={1} /> {activeEdge.type === 'gas' ? 'mcm/d' : 'MW'}
                        </span>
                      </div>
                      <div className="flex justify-between text-sm items-center">
                        <span style={{ color: 'var(--text-secondary)' }}>Current Flow</span>
                        <span className="font-mono text-base font-bold" style={{ color: activeEdge.status === 'offline' ? 'var(--score-red)' : 'var(--text-muted)' }}>
                          <MotionNumber value={activeEdge.status === 'offline' ? 0.0 : activeEdge.cap * 0.7} decimals={1} /> {activeEdge.type === 'gas' ? 'mcm/d' : 'MW'}
                        </span>
                      </div>
                    </div>

                    <div className="mt-2 text-sm">
                      <div className="flex justify-between text-xs mb-2" style={{ color: 'var(--text-secondary)' }}>
                        <span>Capacity Utilization</span>
                        <span className="font-mono font-bold">{activeEdge.status === 'offline' ? '0%' : '70%'}</span>
                      </div>
                      <div className="h-3 w-full bg-[#0f172a] rounded overflow-hidden p-0.5 border border-[#1e293b]">
                        <motion.div 
                          className="h-full rounded-sm" 
                          initial={{ width: 0 }}
                          animate={{ width: activeEdge.status === 'offline' ? '0%' : '70%' }}
                          transition={{ duration: 0.5, ease: "easeOut" }}
                          style={{ background: getStatusColor(activeEdge.status) }}
                        />
                      </div>
                    </div>
                  </motion.div>
                ) : (
                  <motion.div 
                    key="empty"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="flex flex-col items-center justify-center h-64 text-center border-2 border-dashed border-[#334155] rounded-xl bg-[#0f172a50]"
                  >
                    <Info size={32} weight="duotone" className="mb-3 text-[var(--text-secondary)] opacity-50" />
                    <p className="text-sm font-medium" style={{ color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                      Select a transmission corridor<br/>to inspect live telemetry
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>
              
              <div className="mt-12">
                 <h4 className="text-xs font-bold uppercase tracking-wider mb-4 border-b pb-2 border-[#334155]" style={{ color: 'var(--text-secondary)' }}>Facility Legend</h4>
                 <div className="grid grid-cols-2 gap-4 text-xs font-medium" style={{ color: 'var(--text-primary)' }}>
                    <div className="flex items-center gap-2 p-2 rounded bg-opacity-10 bg-white hover:bg-opacity-20 transition-colors"><Atom size={16} weight="duotone" /> Nuclear Base</div>
                    <div className="flex items-center gap-2 p-2 rounded bg-opacity-10 bg-white hover:bg-opacity-20 transition-colors"><Fire size={16} weight="duotone" /> LNG Terminal</div>
                    <div className="flex items-center gap-2 p-2 rounded bg-opacity-10 bg-white hover:bg-opacity-20 transition-colors"><Database size={16} weight="duotone" /> Gas Storage</div>
                    <div className="flex items-center gap-2 p-2 rounded bg-opacity-10 bg-white hover:bg-opacity-20 transition-colors"><Factory size={16} weight="duotone" /> Thermal Plant</div>
                 </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
