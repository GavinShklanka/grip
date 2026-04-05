import { useQuery, useMutation } from '@tanstack/react-query'
import { fetchPrebuiltScenarios, fetchTopology, runScenario } from '../api'
import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { XCircle, Lightning, CheckCircle, Target, WarningDiamond } from '@phosphor-icons/react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine, Cell } from 'recharts'
import MotionNumber from '../components/MotionNumber'

const COUNTRY_LABELS = { EE: 'Estonia', FI: 'Finland', LV: 'Latvia', LT: 'Lithuania' }

const SCENARIO_DESCRIPTIONS = {
  'estlink_fault': 'Simulates an unplanned outage of both Estlink 1 and Estlink 2 cables connecting Finland to Estonia, severely constraining Baltic import capacity.',
  'balticconnector_outage': 'Simulates a severed Balticconnector gas pipeline, removing direct Finland-Estonia gas transmission.',
  'full_nordic_decoupling': 'Models a severe disruption where all Nordic-Baltic interconnectors fail, forcing the Baltics into an islanded macro-grid state.',
  'custom': 'Design a custom disruption by manually disabling specific cross-border transmission corridors.'
}

export default function ScenarioWorkspace() {
  const { data: scenData } = useQuery({ queryKey: ['prebuilt-scenarios'], queryFn: fetchPrebuiltScenarios })
  const { data: topoData } = useQuery({ queryKey: ['topology'], queryFn: fetchTopology })
  
  const [searchParams, setSearchParams] = useSearchParams()
  const selectedId = searchParams.get('scenario') || ''
  
  const [customOverrides, setCustomOverrides] = useState([])
  const [result, setResult] = useState(null)

  const scenarios = scenData?.scenarios ?? []
  const links = topoData?.graph?.links ?? []
  const edgeIds = [...new Set(links.map(l => l.edge_id).filter(Boolean))]

  const mutation = useMutation({
    mutationFn: (payload) => runScenario(payload),
    onSuccess: (data) => setResult(data),
  })

  function handleRun() {
    if (selectedId === 'custom') {
      mutation.mutate({ scenario_id: null, overrides: customOverrides.map(id => ({ edge_id: id, status: 'offline' })) })
    } else if (selectedId) {
      mutation.mutate({ scenario_id: selectedId, overrides: [] })
    }
  }

  function handleSelect(val) {
    if (val) setSearchParams({ scenario: val })
    else setSearchParams({})
    setResult(null)
  }

  function toggleEdge(id) {
    setCustomOverrides(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id])
  }

  const cascadeResults = result?.cascade_results
  const marginsBefore = result?.margins_before || []
  const marginsAfter = result?.margins_after || []

  const chartData = marginsAfter.map(mAfter => {
    const mBefore = marginsBefore.find(b => b.country_id === mAfter.country_id)
    const bVal = mBefore?.margin_mw || 0
    const aVal = mAfter.margin_mw || 0
    const delta = aVal - bVal
    return {
      country: mAfter.country_id,
      before: bVal,
      after: aVal,
      delta: delta
    }
  })

  const totalLostCapacity = chartData.reduce((acc, obj) => Math.min(acc, acc + obj.delta), 0)

  return (
    <div className="max-w-7xl mx-auto px-4 pb-12">
      <h1 className="text-3xl font-bold tracking-tight mb-2" style={{ color: 'var(--text-primary)' }}>Scenario Workspace</h1>
      <p className="text-base mb-6" style={{ color: 'var(--text-secondary)' }}>
        Simulate infrastructure disruptions and trace cascading failures across the Baltic grid.
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 relative">
        {/* Left: Configuration Panel */}
        <div className="lg:col-span-4 card self-start sticky top-6 border border-[var(--border-card)]">
          <div className="flex items-center gap-2 mb-4 pb-3 border-b border-[var(--border-card)]">
            <Target size={24} weight="duotone" className="text-[var(--text-accent)]" />
            <h2 className="text-lg font-bold" style={{ color: 'var(--text-primary)' }}>Simulation Config</h2>
          </div>

          <label className="block text-xs font-semibold mb-2 uppercase tracking-wider" style={{ color: 'var(--text-secondary)' }}>Target Scenario</label>
          <select
            className="w-full px-3 py-2 rounded text-sm mb-4 outline-none font-semibold transition-colors appearance-none cursor-pointer"
            style={{ background: 'var(--bg-primary)', color: 'var(--text-primary)', border: `1px solid ${selectedId ? 'var(--text-accent)' : 'var(--border)'}` }}
            value={selectedId}
            onChange={(e) => handleSelect(e.target.value)}
          >
            <option value="">Choose scenario framework...</option>
            {scenarios.map(s => (
              <option key={s.id || s} value={s.id || s}>{(s.name || s.id || s).replace(/_/g, ' ').toUpperCase()}</option>
            ))}
            <option value="custom">⚙ CUSTOM OVERRIDE</option>
          </select>

          <AnimatePresence mode="popLayout">
            {selectedId && (
              <motion.div 
                initial={{ opacity: 0, height: 0 }} 
                animate={{ opacity: 1, height: 'auto' }} 
                exit={{ opacity: 0, height: 0 }}
                className="overflow-hidden"
              >
                <div className="p-3 rounded mb-4 text-sm leading-relaxed border border-[var(--border-card)]" style={{ background: 'var(--bg-secondary)', color: 'var(--text-secondary)' }}>
                  {SCENARIO_DESCRIPTIONS[selectedId] || 'Custom infrastructure selection mode.'}
                </div>
              </motion.div>
            )}

            {selectedId === 'custom' && (
              <motion.div 
                initial={{ opacity: 0, height: 0 }} 
                animate={{ opacity: 1, height: 'auto' }} 
                exit={{ opacity: 0, height: 0 }}
                className="space-y-1 mb-6 p-4 rounded border border-[var(--border-card)] overflow-hidden" 
                style={{ background: 'var(--bg-secondary)' }}
              >
                <p className="text-xs mb-3 font-semibold uppercase tracking-wider" style={{ color: 'var(--text-primary)' }}>Disable Corridors</p>
                <div className="max-h-48 overflow-y-auto space-y-2 pr-2 custom-scrollbar">
                  {edgeIds.map(id => (
                    <label key={id} className={`flex items-center gap-3 text-sm cursor-pointer p-2 rounded transition-colors ${customOverrides.includes(id) ? 'bg-red-900 bg-opacity-20 border-red-500 border border-opacity-30 flex-row-reverse justify-between' : 'hover:bg-[var(--bg-primary)] border border-transparent'}`}>
                      <input type="checkbox" checked={customOverrides.includes(id)}
                        onChange={() => toggleEdge(id)}
                        className="w-4 h-4 rounded appearance-none ring-1 ring-[#334155] checked:bg-[var(--score-red)] checked:ring-[var(--score-red)] cursor-pointer transition-colors" />
                      <div className="flex flex-col">
                        <span className="font-mono tracking-tight" style={{ color: customOverrides.includes(id) ? 'var(--score-red)' : 'var(--text-primary)' }}>
                          {id.replace(/_/g, ' ').toUpperCase()}
                        </span>
                        {customOverrides.includes(id) && <span className="text-xs text-[var(--score-red)] opacity-80">Link forced offline</span>}
                      </div>
                    </label>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <button
            onClick={handleRun}
            disabled={!selectedId || mutation.isPending}
            className="w-full mt-2 py-3 rounded-lg text-sm font-bold uppercase tracking-wider transition-all shadow-lg flex justify-center items-center gap-2"
            style={{
              background: mutation.isPending ? 'var(--bg-secondary)' : (selectedId ? 'var(--text-accent)' : 'var(--bg-secondary)'),
              color: selectedId && !mutation.isPending ? 'var(--bg-primary)' : 'var(--text-muted)',
              border: '1px solid transparent',
              cursor: selectedId && !mutation.isPending ? 'pointer' : 'not-allowed'
            }}
          >
            {mutation.isPending && <div className="w-4 h-4 rounded-full border-2 border-r-transparent animate-spin" style={{ borderColor: 'var(--text-muted)', borderRightColor: 'transparent' }}></div>}
            {mutation.isPending ? 'Executing...' : 'Execute Simulation'}
          </button>
        </div>

        {/* Right: Telemetry Results */}
        <div className="lg:col-span-8 flex flex-col gap-6 relative">
          <AnimatePresence mode="wait">
            {!result ? (
              <motion.div key="empty" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="card h-full flex flex-col items-center justify-center py-32 border border-dashed border-[var(--border-card)]" style={{ background: 'var(--bg-primary)' }}>
                <div className="w-16 h-16 rounded-full flex items-center justify-center mb-4" style={{ background: 'var(--bg-secondary)' }}>
                  <Lightning size={32} weight="duotone" className="opacity-50" />
                </div>
                <h3 className="text-lg font-bold" style={{ color: 'var(--text-primary)' }}>Awaiting Simulation</h3>
                <p className="text-sm mt-2 text-center max-w-sm" style={{ color: 'var(--text-secondary)' }}>
                  Configure parameters and execute to render cascade trace and delta margins.
                </p>
              </motion.div>
            ) : (
              <motion.div key="results" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="flex flex-col gap-6 w-full">
                
                <div className="flex bg-[#ef444410] border border-[var(--score-red)] rounded-lg p-5">
                   <div className="flex flex-col flex-1">
                     <h3 className="text-sm font-bold uppercase tracking-wider mb-3" style={{ color: 'var(--score-red)' }}>Incident Manifest</h3>
                     <div className="flex flex-wrap gap-3">
                       {(result.applied_overrides ?? []).map((o, i) => (
                         <div key={i} className="flex items-center gap-2 px-3 py-2 rounded-md text-xs font-mono font-bold"
                           style={{ background: '#ef444420', color: 'var(--score-red)', border: '1px solid #ef444440' }}>
                           <XCircle size={16} weight="fill" />
                           {o.edge_id.toUpperCase()} <span className="opacity-50">→</span> {o.status.toUpperCase()}
                         </div>
                       ))}
                       {(result.applied_overrides?.length === 0) && (
                         <span className="text-sm" style={{ color: 'var(--text-muted)' }}>No explicit overrides generated.</span>
                       )}
                     </div>
                   </div>
                   <div className="flex flex-col items-end border-l border-[#ef444430] pl-6 ml-4 justify-center">
                      <span className="text-xs uppercase tracking-wider font-bold mb-1" style={{ color: 'var(--score-red)' }}>System Impact</span>
                      <span className="font-mono text-3xl font-black tracking-tighter" style={{ color: 'var(--score-red)' }}>{totalLostCapacity.toFixed(0)} MW</span>
                   </div>
                </div>

                {/* Grid Margin Deltas */}
                {marginsAfter.length > 0 && (
                  <div className="card shadow-lg bg-[var(--bg-card)]">
                    <h3 className="text-sm font-bold uppercase tracking-wider mb-4" style={{ color: 'var(--text-primary)' }}>Before/After N-1 Grid Margin</h3>
                    
                    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-6">
                      {chartData.map((d, i) => (
                        <motion.div 
                          key={d.country} 
                          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}
                          className="p-4 rounded-lg flex flex-col border border-[var(--border-card)]" 
                          style={{ background: 'var(--bg-primary)' }}
                        >
                          <span className="text-sm font-bold mb-3" style={{ color: 'var(--text-primary)' }}>{COUNTRY_LABELS[d.country] || d.country}</span>
                          <div className="grid grid-cols-2 gap-2 text-xs mb-3">
                             <div className="flex flex-col">
                               <span style={{ color: 'var(--text-secondary)' }}>Before</span>
                               <span className="font-mono font-bold" style={{ color: 'var(--text-primary)' }}>{d.before.toFixed(0)} MW</span>
                             </div>
                             <div className="flex flex-col items-end">
                               <span style={{ color: 'var(--text-secondary)' }}>After</span>
                               <span className="font-mono font-bold" style={{ color: d.after >= 0 ? 'var(--score-green)' : 'var(--score-red)' }}>{d.after.toFixed(0)} MW</span>
                             </div>
                          </div>
                          <div className={`mt-auto py-2 px-3 rounded flex items-center justify-between border ${d.delta < 0 ? 'bg-[#ef444410] border-[#ef444430]' : 'bg-[#22c55e10] border-[#22c55e30]'}`}>
                            <span className="text-xs font-bold uppercase" style={{ color: d.delta < 0 ? 'var(--score-red)' : 'var(--score-green)' }}>Delta</span>
                            <span className="text-sm font-mono font-bold" style={{ color: d.delta < 0 ? 'var(--score-red)' : 'var(--score-green)' }}>
                              {d.delta > 0 ? '+' : ''}<MotionNumber value={d.delta} decimals={0} /> MW
                            </span>
                          </div>
                        </motion.div>
                      ))}
                    </div>

                    {/* Waterfall visual */}
                    <div className="h-56 pt-2 pb-2">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={chartData} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                          <XAxis dataKey="country" stroke="var(--text-secondary)" fontSize={12} tickLine={false} axisLine={false} />
                          <YAxis stroke="var(--text-secondary)" fontSize={12} tickLine={false} axisLine={false} />
                          <Tooltip 
                            cursor={{ fill: 'var(--bg-secondary)' }}
                            contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '8px' }} 
                            content={({ active, payload }) => {
                              if (!active || !payload || !payload.length) return null;
                              const { country, after, delta } = payload[0].payload;
                              return (
                                <div className="p-3 bg-[var(--bg-card)] border border-[var(--border-card)] rounded shadow-xl min-w-[150px]">
                                   <div className="font-bold mb-2">{COUNTRY_LABELS[country] || country}</div>
                                   <div className="flex justify-between text-sm font-mono mb-1">
                                      <span className="text-[var(--text-secondary)]">Margin:</span>
                                      <span className="font-bold" style={{ color: after < 0 ? 'var(--score-red)' : 'var(--text-primary)'}}>{after.toFixed(0)}</span>
                                   </div>
                                   <div className="flex justify-between text-sm font-mono">
                                      <span className="text-[var(--text-secondary)]">Delta:</span>
                                      <span className="font-bold" style={{ color: delta < 0 ? 'var(--score-red)' : 'var(--score-green)'}}>{delta.toFixed(0)}</span>
                                   </div>
                                </div>
                              )
                            }}
                          />
                          <ReferenceLine y={0} stroke="var(--border-card)" strokeDasharray="3 3"/>
                          <Bar dataKey="after" radius={[4, 4, 0, 0]} maxBarSize={60}>
                            {chartData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.after >= 0 ? 'var(--score-green)' : 'var(--score-red)'} />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                )}

                {/* Cascade Execution Log */}
                {cascadeResults && cascadeResults.cascade_log?.length > 0 && (
                  <div className="card bg-[var(--bg-card)]">
                    <div className="flex justify-between items-center mb-6">
                      <h3 className="text-sm font-bold uppercase tracking-wider flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
                        Cascade Trace Sequence
                      </h3>
                      <span className="text-xs font-mono px-3 py-1.5 rounded font-bold" style={{ background: '#f59e0b20', color: 'var(--score-amber)' }}>
                        {cascadeResults.equilibrium_steps} STEPS TO EQUILIBRIUM
                      </span>
                    </div>

                    <div className="space-y-0 text-sm font-mono border-l-2 border-[#334155] ml-4 pt-2">
                      <AnimatePresence>
                        {cascadeResults.cascade_log.map((step, i) => {
                          const keys = Object.keys(step);
                          return (
                            <motion.div 
                              key={i} 
                              initial={{ opacity: 0, x: -15 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.15 }}
                              className="pl-8 pb-8 relative"
                            >
                              <div className="absolute left-[-13px] top-0.5 bg-[var(--bg-card)] p-1">
                                <WarningDiamond size={16} weight="fill" className="text-[var(--text-secondary)]" />
                              </div>
                              <div className="text-xs font-bold uppercase tracking-wider mb-2" style={{ color: 'var(--text-secondary)' }}>Propagation Step {i + 1}</div>
                              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                 {keys.map(k => (
                                    <div key={k} className="p-3 rounded-lg border border-[var(--border-card)]" style={{ background: 'var(--bg-primary)' }}>
                                       <div className="text-xs uppercase mb-1" style={{ color: 'var(--text-secondary)' }}>Target Filter</div>
                                       <div className="font-mono text-sm leading-relaxed" style={{ color: 'var(--score-red)' }}>{k} : {step[k]}</div>
                                    </div>
                                 ))}
                              </div>
                            </motion.div>
                          )
                        })}
                      </AnimatePresence>
                      <motion.div 
                        initial={{ opacity: 0, x: -15 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: cascadeResults.cascade_log.length * 0.15 }}
                        className="pl-8 relative pt-2"
                      >
                         <div className="absolute left-[-13px] top-2 bg-[var(--bg-card)] p-1">
                           <CheckCircle size={16} weight="fill" className="text-[var(--score-green)]" />
                         </div>
                         <div className="text-sm font-bold uppercase tracking-wider" style={{ color: 'var(--score-green)' }}>Grid Stabilized</div>
                      </motion.div>
                    </div>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}
