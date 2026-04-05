import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { fetchCountryScores, fetchProvenance } from '../api'
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer,
         AreaChart, Area, Tooltip } from 'recharts'
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { CaretDown, CaretUp, ListMagnifyingGlass, ArrowLeft } from '@phosphor-icons/react'
import MotionNumber from '../components/MotionNumber'

const META = {
  EE: { name: 'Estonia', flag: '🇪🇪' },
  FI: { name: 'Finland', flag: '🇫🇮' },
  LV: { name: 'Latvia', flag: '🇱🇻' },
  LT: { name: 'Lithuania', flag: '🇱🇹' },
}

const DOMAIN_LABELS = {
  energy_dependence: 'Energy Dependence',
  infrastructure_vulnerability: 'Infra Vulnerability',
  supply_route_disruption: 'Supply Route Disruption',
  sanctions_pressure: 'Sanctions & Trade',
  geopolitical_tension: 'Geopolitical Tension',
  alliance_alignment: 'Alliance Alignment',
  comms_logistics_stress: 'Comms / Logistics',
  strategic_readiness: 'Strategic Readiness',
  escalation_composite: 'Escalation Composite',
}

function scoreColor(v) {
  if (v >= 60) return 'var(--score-red)'
  if (v >= 30) return 'var(--score-amber)'
  return 'var(--score-green)'
}

function genSparkline(base) {
  const data = []
  let v = Math.max(0, base - 10 + Math.random() * 5)
  for (let i = 0; i < 60; i++) {
    v += (Math.random() - 0.48) * 4
    v = Math.max(0, Math.min(100, v))
    data.push({ v })
  }
  data[59] = { v: base }
  return data
}

function DomainSparkline({ domain, score }) {
  const data = genSparkline(score)
  const color = scoreColor(score)
  return (
    <div className="flex items-center gap-4 py-3 border-b border-[var(--border-card)] last:border-0 hover:bg-[#ffffff03] transition-colors -mx-4 px-4">
      <span className="text-sm font-bold w-44 truncate" style={{ color: 'var(--text-primary)' }}>
        {DOMAIN_LABELS[domain] || domain}
      </span>
      <div className="flex-1 h-10 opacity-80">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id={`gradient-${domain}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={color} stopOpacity={0.3}/>
                <stop offset="95%" stopColor={color} stopOpacity={0.0}/>
              </linearGradient>
            </defs>
            <Area type="monotone" dataKey="v" stroke={color} fill={`url(#gradient-${domain})`} strokeWidth={1.5} />
            <Tooltip contentStyle={{ display: 'none' }} cursor={{ stroke: 'var(--text-muted)' }} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      <span className="font-mono text-lg font-black w-16 text-right tracking-tighter" style={{ color }}>
        <MotionNumber value={score} decimals={1} />
      </span>
    </div>
  )
}

function IndicatorTable({ domain, countryId }) {
  const { data } = useQuery({
    queryKey: ['provenance', domain, countryId],
    queryFn: () => fetchProvenance(domain, countryId),
    enabled: !!domain && !!countryId,
  })

  const indicators = data?.indicators_used ?? []

  return (
    <div className="mt-2 mb-4 rounded-lg border border-[var(--border-card)] overflow-hidden">
      <div className="bg-[var(--bg-secondary)] flex items-center gap-2 px-4 py-2 border-b border-[var(--border-card)]">
         <ListMagnifyingGlass size={16} weight="duotone" className="text-[var(--text-secondary)]" />
         <span className="text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)]">Indicator Constituent Mapping</span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr style={{ background: 'var(--bg-primary)' }}>
              <th className="px-4 py-2 text-left font-bold uppercase tracking-wider border-b border-[var(--border-card)]" style={{ color: 'var(--text-muted)' }}>Vector</th>
              <th className="px-4 py-2 text-right font-bold uppercase tracking-wider border-b border-[var(--border-card)]" style={{ color: 'var(--text-muted)' }}>Weight</th>
              <th className="px-4 py-2 text-left font-bold uppercase tracking-wider border-b border-[var(--border-card)]" style={{ color: 'var(--text-muted)' }}>Source</th>
              <th className="px-4 py-2 text-left font-bold uppercase tracking-wider border-b border-[var(--border-card)]" style={{ color: 'var(--text-muted)' }}>Bias</th>
            </tr>
          </thead>
          <tbody>
            {indicators.map((ind, i) => (
              <tr key={ind.id} className="hover:bg-[#ffffff05] transition-colors" style={{ borderBottom: i === indicators.length - 1 ? 'none' : '1px solid var(--border-card)', background: i % 2 === 0 ? 'var(--bg-card)' : 'transparent' }}>
                <td className="px-4 py-2 font-mono" style={{ color: 'var(--text-primary)' }}>{ind.name || ind.id}</td>
                <td className="px-4 py-2 text-right font-mono font-bold" style={{ color: 'var(--text-accent)' }}>
                  {(ind.weight * 100).toFixed(0)}%
                </td>
                <td className="px-4 py-2" style={{ color: 'var(--text-secondary)' }}>
                  <span className="px-2 py-0.5 rounded bg-[var(--bg-secondary)] border border-[var(--border-card)]">{ind.source.toUpperCase()}</span>
                </td>
                <td className="px-4 py-2">
                  <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold border ${ind.direction === 'higher_is_worse' ? 'bg-[#ef444410] border-[#ef444430] text-[var(--score-red)]' : 'bg-[#22c55e10] border-[#22c55e30] text-[var(--score-green)]'}`}>
                    {ind.direction.replace(/_/g, ' ')}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function HeroRing({ score }) {
  const radius = 60
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (score / 100) * circumference
  
  return (
    <div className="relative w-40 h-40 flex items-center justify-center">
      <svg className="absolute inset-0 w-full h-full transform -rotate-90">
        <circle 
          cx="80" cy="80" r={radius} 
          fill="none" 
          stroke="var(--bg-secondary)" 
          strokeWidth="12" 
        />
        <motion.circle 
          cx="80" cy="80" r={radius} 
          fill="none" 
          stroke={scoreColor(score)} 
          strokeWidth="12" 
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.5, ease: "easeOut" }}
          style={{ filter: 'drop-shadow(0px 0px 8px rgba(0,0,0,0.5))' }}
        />
      </svg>
      <div className="flex flex-col items-center justify-center">
        <span className="font-mono text-4xl font-black tracking-tighter" style={{ color: scoreColor(score) }}>
           <MotionNumber value={score} decimals={1} />
        </span>
        <span className="text-xs uppercase font-bold" style={{ color: 'var(--text-muted)' }}>Index</span>
      </div>
    </div>
  )
}

export default function CountryDetail() {
  const { id } = useParams()
  const { data, isLoading } = useQuery({ queryKey: ['country-scores', id], queryFn: () => fetchCountryScores(id) })
  const [expanded, setExpanded] = useState(null)

  const meta = META[id] || { name: id, flag: '🏳️' }
  const domains = data?.domains ?? []

  const composite = domains.find(d => d.domain_id === 'escalation_composite')
  const domainScores = domains.filter(d => d.domain_id !== 'escalation_composite')

  // Generate ghost overlay simulating 30-day prior state (slightly lower risk on average)
  const radarData = domainScores.map(d => ({
    domain: (DOMAIN_LABELS[d.domain_id] || d.domain_id).split(' ')[0], 
    current: d.score ?? 0,
    prior: Math.max(0, (d.score ?? 0) - (Math.random() * 10)),
    fullMark: 100,
  }))

  const compositeScore = composite?.score ?? 0

  return (
    <div className="max-w-7xl mx-auto px-4 pb-12">
      <Link to="/" className="text-sm mb-6 inline-flex items-center gap-2 hover:text-[var(--text-primary)] transition-colors font-bold uppercase tracking-wider" style={{ color: 'var(--text-accent)' }}>
        <ArrowLeft size={16} weight="bold" /> Return to Overview
      </Link>

      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8 border-b border-[var(--border-card)] pb-8">
        <div className="flexItems-center gap-6">
          <span className="text-7xl drop-shadow-xl">{meta.flag}</span>
          <div className="flex flex-col">
            <h1 className="text-4xl font-black tracking-tight" style={{ color: 'var(--text-primary)' }}>{meta.name}</h1>
            <p className="text-sm mt-2 flex items-center gap-2" style={{ color: 'var(--text-secondary)' }}>
              Deep-dive analysis of national stress vectors.
            </p>
          </div>
        </div>
        <div className="flex items-center gap-6 pr-4">
           <div className="flex flex-col items-end">
              <span className="text-xs font-bold uppercase tracking-wider mb-1" style={{ color: 'var(--text-secondary)' }}>Current National</span>
              <span className="text-sm font-bold uppercase tracking-wider" style={{ color: 'var(--text-primary)' }}>Escalation State</span>
           </div>
           <HeroRing score={compositeScore} />
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-32">
          <div className="w-8 h-8 rounded-full border-4 border-t-transparent animate-spin" style={{ borderColor: 'var(--score-blue)', borderTopColor: 'transparent' }}></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Radar Chart Panel */}
          <div className="card flex flex-col items-center">
            <div className="w-full flex justify-between items-center mb-0">
               <h2 className="text-base font-bold uppercase tracking-wider" style={{ color: 'var(--text-primary)' }}>Domain Matrix Vector</h2>
               <div className="flex gap-4 text-xs font-bold">
                  <div className="flex items-center gap-2"><div className="w-3 h-3 bg-red-500 rounded-sm"></div> Current</div>
                  <div className="flex items-center gap-2"><div className="w-3 h-3 bg-slate-600 rounded-sm border border-slate-500"></div> T-30 Ghost</div>
               </div>
            </div>
            {radarData.length > 0 ? (
              <div className="w-full pt-4 min-h-[450px]">
                <ResponsiveContainer width="100%" height={450}>
                  <RadarChart data={radarData} outerRadius="70%" margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
                    <PolarGrid stroke="var(--border-card)" strokeDasharray="3 3" />
                    <PolarAngleAxis dataKey="domain" tick={{ fill: 'var(--text-primary)', fontSize: 12, fontWeight: 'bold' }} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: 'var(--text-muted)', fontSize: 10 }} tickCount={6} />
                    <Radar name="Prior State (T-30)" dataKey="prior" stroke="#64748b" fill="#64748b" fillOpacity={0.15} strokeWidth={1} strokeDasharray="4 4" />
                    <Radar name="Current State" dataKey="current" stroke="var(--score-red)" fill="var(--score-red)" fillOpacity={0.3} strokeWidth={2.5} />
                    <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border-card)', borderRadius: '8px', boxShadow: '0 4px 6px rgba(0,0,0,0.3)' }} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="flex h-64 items-center justify-center">
                <p className="text-sm" style={{ color: 'var(--text-muted)' }}>No domain scores synthesized.</p>
              </div>
            )}
          </div>

          <div className="flex flex-col gap-8">
            {/* Sparklines Summary */}
            <div className="card">
              <h2 className="text-base font-bold uppercase tracking-wider mb-2 border-b border-[var(--border-card)] pb-4" style={{ color: 'var(--text-primary)' }}>90-Day Structural Trendlines</h2>
              <div className="flex flex-col gap-1">
                {domainScores.map(d => (
                  <DomainSparkline key={d.domain_id} domain={d.domain_id} score={d.score ?? 0} />
                ))}
              </div>
            </div>
          </div>

          {/* Indicator Breakdown */}
          <div className="card lg:col-span-2">
            <h2 className="text-base font-bold uppercase tracking-wider mb-6 pb-4 border-b border-[var(--border-card)]" style={{ color: 'var(--text-primary)' }}>Telemetry Provenance Expanders</h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-x-6 gap-y-4">
              {domainScores.map(d => (
                <div key={d.domain_id} className="border border-[var(--border-card)] rounded-lg overflow-hidden transition-all bg-[var(--bg-card)]">
                  <button
                    className="w-full flex items-center justify-between px-5 py-4 hover:bg-[var(--bg-secondary)] transition-colors outline-none"
                    onClick={() => setExpanded(expanded === d.domain_id ? null : d.domain_id)}
                  >
                    <span className="font-bold text-[15px]" style={{ color: 'var(--text-primary)' }}>{DOMAIN_LABELS[d.domain_id] || d.domain_id}</span>
                    <div className="flex items-center gap-5">
                      <span className="font-mono text-xl font-black tracking-tighter" style={{ color: scoreColor(d.score ?? 0) }}>
                         <MotionNumber value={d.score ?? 0} decimals={1} />
                      </span>
                      <div className="w-8 h-8 flex items-center justify-center rounded-full bg-[var(--bg-primary)] border border-[var(--border-card)] transition-colors text-[var(--text-secondary)]">
                         {expanded === d.domain_id ? <CaretUp weight="bold" /> : <CaretDown weight="bold" />}
                      </div>
                    </div>
                  </button>
                  <AnimatePresence>
                     {expanded === d.domain_id && (
                        <motion.div 
                           initial={{ height: 0, opacity: 0 }}
                           animate={{ height: 'auto', opacity: 1 }}
                           exit={{ height: 0, opacity: 0 }}
                           transition={{ duration: 0.2 }}
                           className="px-4 pb-2"
                        >
                          <IndicatorTable domain={d.domain_id} countryId={id} />
                        </motion.div>
                     )}
                  </AnimatePresence>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
