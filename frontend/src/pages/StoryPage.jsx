import { useRef } from 'react'
import { Link } from 'react-router-dom'
import { motion, useInView, useSpring, useTransform } from 'framer-motion'
import { useEffect } from 'react'
import {
  Monitor, Graph, Target, BookOpen, ArrowDown, Lightning,
  Buildings, Globe, MapTrifold,
  Atom, Drop, Export, GithubLogo, FileText,
  ArrowRight
} from '@phosphor-icons/react'

/* ── helpers ────────────────────────────────────────────────── */

function Section({ children, className = '', delay = 0 }) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-80px' })
  return (
    <motion.section
      ref={ref}
      initial={{ opacity: 0, y: 40 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.7, delay, ease: 'easeOut' }}
      className={className}
    >
      {children}
    </motion.section>
  )
}

function AnimatedCounter({ target, suffix = '', duration = 2 }) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true })
  const spring = useSpring(0, { stiffness: 30, damping: 25 })
  const display = useTransform(spring, v => Math.round(v).toLocaleString())

  useEffect(() => {
    if (inView) spring.set(target)
  }, [inView, target, spring])

  return (
    <span ref={ref} className="inline-flex items-baseline gap-2">
      <motion.span className="font-mono text-7xl md:text-8xl font-black tracking-tighter text-white">
        {display}
      </motion.span>
      {suffix && <span className="text-2xl md:text-3xl font-bold text-[var(--text-muted)]">{suffix}</span>}
    </span>
  )
}

/* ── data ───────────────────────────────────────────────────── */

const TIMELINE_EVENTS = [
  { date: '2022-09-26', name: 'Nord Stream explosions', desc: 'Subsea pipelines sabotaged in coordinated attack', type: 'other' },
  { date: '2022-10-07', name: 'Balticconnector cable damage', desc: 'Finland-Estonia gas pipeline damaged by external force', type: 'energy' },
  { date: '2023-10-08', name: 'Balticconnector anchor strike', desc: 'Chinese vessel anchor dragged across gas pipeline', type: 'energy' },
  { date: '2023-10-08', name: 'Estonia-Finland telecom cut', desc: 'Submarine telecom cable severed simultaneously', type: 'other' },
  { date: '2024-01-26', name: 'Estlink 2 technical fault', desc: 'HVDC cable between Finland-Estonia offline for months', type: 'energy' },
  { date: '2024-11-17', name: 'NordBalt suspected damage', desc: 'Sweden-Lithuania power cable damaged by vessel', type: 'energy' },
  { date: '2024-11-18', name: 'C-Lion1 telecom cable cut', desc: 'Finland-Germany subsea telecom cable severed', type: 'other' },
  { date: '2024-12-25', name: 'Eagle S — Estlink 2 severance', desc: 'Shadow fleet tanker dragged anchor 90km, cutting power cable', type: 'energy' },
  { date: '2024-12-25', name: 'Multiple telecom cables cut', desc: 'Four additional submarine cables damaged in same incident', type: 'other' },
  { date: '2025-01-26', name: 'Estlink 1 emergency repair', desc: 'Remaining Finland-Estonia cable at max capacity', type: 'energy' },
  { date: '2025-09-01', name: 'Estlink 1 planned outage', desc: 'All HVDC capacity to Estonia temporarily zero', type: 'energy' },
  { date: '2026-01-20', name: 'Kiisa battery facility fault', desc: 'Major Estonian grid stabilization asset offline', type: 'other' },
]

const STAT_CARDS = [
  { value: '12', label: 'infrastructure attacks or failures in 4 years' },
  { value: '6', label: 'critical energy interconnector disruptions' },
  { value: '3', label: 'countries dependent on a serial chain of cables' },
  { value: '1', label: 'synchronous power connection to the rest of Europe' },
]

const GRIP_CARDS = [
  {
    title: 'Monitor',
    icon: Monitor,
    link: '/',
    desc: 'Tracks 27 indicators across 8 risk domains for Finland, Estonia, Latvia, and Lithuania. Produces daily risk scores so analysts can see stress building before it becomes a crisis.',
  },
  {
    title: 'Map',
    icon: MapTrifold,
    link: '/topology',
    desc: "Models the physical infrastructure — every cable, pipeline, and power plant — as a dependency network. Shows exactly which connections each country relies on.",
  },
  {
    title: 'Simulate',
    icon: Target,
    link: '/scenario',
    desc: "Lets analysts ask 'what if?' — remove a cable, shut down a pipeline, simulate a multi-infrastructure attack — and see the cascade consequences in seconds.",
  },
  {
    title: 'Validate',
    icon: BookOpen,
    link: '/methodology',
    desc: "Tests itself against history. GRIP's risk model detected all 6 major disruption events in backtesting. Every score is traceable to its source. Every limitation is documented.",
  },
]

const FINDINGS = [
  { metric: 'Events detected', value: '6 / 6', meaning: 'The model flagged elevated risk before every major disruption' },
  { metric: 'Risk domains', value: '8 + 1 composite', meaning: 'Energy, infrastructure, supply routes, sanctions, geopolitics, alliance, comms, readiness' },
  { metric: 'Scenario types', value: '6 pre-built', meaning: 'Cable severance, pipeline damage, multi-attack, LNG shock, sanctions escalation, grid isolation' },
  { metric: 'Backtesting events', value: '12', meaning: 'Real-world disruptions used to validate the model (2022–2026)' },
  { metric: 'Data sources', value: '7', meaning: 'ENTSO-E, ENTSOG, GDELT, OpenSanctions, Eurostat, Copernicus, SIPRI' },
]

const CANADA_CARDS = [
  {
    title: 'LNG Diversification',
    icon: Drop,
    body: "Canadian LNG loosens the global market, freeing cargos for Europe. The Baltics have 8.75 bcm/year of LNG intake capacity waiting for diversified supply.",
  },
  {
    title: 'Nuclear Partnership',
    icon: Atom,
    body: "Canada produces 24% of the world's uranium. Estonia is actively studying Canadian SMR technology. Nuclear fuel-cycle services are a decades-long partnership, not a commodity sale.",
  },
  {
    title: 'Resilience Analytics',
    icon: Export,
    body: "GRIP itself is an exportable Canadian product. The same architecture — topology modeling, disruption scoring, scenario simulation — applies to any corridor with chokepoint vulnerability.",
  },
]

/* ── main component ─────────────────────────────────────────── */

export default function StoryPage() {
  return (
    <div className="max-w-6xl mx-auto px-4 -mt-6">

      {/* ═══ SECTION 1 — THE HOOK ═══ */}
      <section className="min-h-[85vh] flex flex-col justify-center items-center text-center relative">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: 'easeOut' }}
          className="max-w-4xl space-y-6"
        >
          <p className="text-lg md:text-xl font-medium uppercase tracking-[0.25em] text-[var(--text-muted)] mb-4">
            Christmas Day 2024
          </p>
          <h1 className="text-3xl md:text-5xl lg:text-[3.4rem] font-black leading-[1.15] tracking-tight text-white">
            A single oil tanker dragged its anchor<br className="hidden md:inline" /> for 90 kilometers across the bottom<br className="hidden md:inline" /> of the Baltic Sea.
          </h1>
          <p className="text-xl md:text-2xl leading-relaxed text-[var(--text-secondary)] max-w-3xl mx-auto mt-8">
            It severed the main power cable between Finland and Estonia.{' '}
            <span className="text-white font-bold">Three countries lost 65% of their electricity import capacity in one hour.</span>
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1, duration: 1 }}
          className="mt-16 flex flex-col items-center gap-3"
        >
          <AnimatedCounter target={650} suffix="MW" />
          <p className="text-base text-[var(--text-muted)] font-medium">
            megawatts lost — enough to power <span className="text-[var(--text-secondary)]">400,000 homes</span>
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2, duration: 1 }}
          className="absolute bottom-8 flex flex-col items-center gap-2"
        >
          <span className="text-xs uppercase tracking-widest text-[var(--text-muted)]">Scroll to continue</span>
          <ArrowDown size={20} className="text-[var(--text-muted)] animate-bounce" />
        </motion.div>
      </section>

      {/* ═══ SECTION 2 — THE PATTERN ═══ */}
      <Section className="py-24 border-t border-[var(--border)]">
        <h2 className="text-3xl md:text-4xl font-black tracking-tight text-center mb-4">
          This wasn't an isolated event.
        </h2>
        <p className="text-center text-[var(--text-secondary)] mb-16 text-lg max-w-2xl mx-auto">
          The Baltic energy corridor has experienced 12 infrastructure disruptions in 4 years — a tempo of sabotage and failure unmatched anywhere in Europe.
        </p>

        {/* Timeline */}
        <div className="relative mb-20">
          {/* Horizontal line */}
          <div className="absolute top-[14px] left-0 right-0 h-[2px] bg-[var(--border)]" />

          <div className="flex justify-between overflow-x-auto pb-4 gap-0 relative" style={{ minWidth: '100%' }}>
            {TIMELINE_EVENTS.map((evt, i) => (
              <div key={i} className="group relative flex flex-col items-center flex-shrink-0" style={{ width: `${100 / TIMELINE_EVENTS.length}%` }}>
                {/* Dot */}
                <div
                  className="w-[10px] h-[10px] rounded-full border-2 z-10 cursor-pointer transition-transform group-hover:scale-[1.8]"
                  style={{
                    borderColor: evt.type === 'energy' ? 'var(--score-red)' : 'var(--score-amber)',
                    background: evt.type === 'energy' ? 'var(--score-red)' : 'var(--score-amber)',
                  }}
                />
                {/* Year label */}
                <span className="text-[10px] font-mono text-[var(--text-muted)] mt-2">
                  {evt.date.slice(0, 4)}
                </span>

                {/* Hover tooltip */}
                <div className="absolute top-8 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-40 w-56">
                  <div className="bg-[var(--bg-card)] border border-[var(--border-card)] rounded-lg p-3 shadow-2xl mt-2">
                    <p className="text-xs font-bold text-white mb-1">{evt.name}</p>
                    <p className="text-[11px] text-[var(--text-muted)] leading-snug">{evt.desc}</p>
                    <p className="text-[10px] font-mono text-[var(--text-muted)] mt-2">{evt.date}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Legend */}
          <div className="flex justify-center gap-6 mt-4 text-xs font-bold">
            <span className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-[var(--score-red)]" /> Energy interconnector
            </span>
            <span className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-[var(--score-amber)]" /> Other infrastructure
            </span>
          </div>
        </div>

        {/* Stat cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {STAT_CARDS.map((s, i) => (
            <Section key={i} delay={i * 0.1} className="card text-center p-6 hover:!bg-[var(--bg-card)]">
              <span className="font-mono text-5xl font-black tracking-tighter text-white block mb-3">
                {s.value}
              </span>
              <span className="text-sm text-[var(--text-secondary)] leading-snug">{s.label}</span>
            </Section>
          ))}
        </div>
      </Section>

      {/* ═══ SECTION 3 — WHY IT MATTERS ═══ */}
      <Section className="py-24 border-t border-[var(--border)]">
        <h2 className="text-3xl md:text-4xl font-black tracking-tight text-center mb-4">
          Why it matters
        </h2>
        <p className="text-center text-[var(--text-secondary)] mb-14 text-lg max-w-2xl mx-auto">
          Infrastructure sabotage isn't abstract. It changes the price of heat, the stability of governments, and the security of global trade.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Section delay={0} className="card p-6 border-t-2 border-t-[var(--score-amber)] hover:!bg-[var(--bg-card)]">
            <div className="flex items-center gap-3 mb-4">
              <Lightning size={28} weight="duotone" className="text-[var(--score-amber)]" />
              <h3 className="text-lg font-bold text-white">For People</h3>
            </div>
            <p className="text-sm leading-relaxed text-[var(--text-secondary)]">
              When Estlink 2 went offline, Estonian electricity prices spiked. For a country of 1.3 million people, every cable outage means higher heating bills in winter, industrial slowdowns, and uncertainty about whether the lights stay on.
            </p>
          </Section>

          <Section delay={0.1} className="card p-6 border-t-2 border-t-[var(--score-red)] hover:!bg-[var(--bg-card)]">
            <div className="flex items-center gap-3 mb-4">
              <Buildings size={28} weight="duotone" className="text-[var(--score-red)]" />
              <h3 className="text-lg font-bold text-white">For Governments</h3>
            </div>
            <p className="text-sm leading-relaxed text-[var(--text-secondary)]">
              The Baltic states desynchronized from Russia's power grid in February 2025 — a historic step for sovereignty. But it means they now rely on a single overland power line to Poland (LitPol Link) for grid stability. If that line fails, three EU member states operate in emergency island mode.
            </p>
          </Section>

          <Section delay={0.2} className="card p-6 border-t-2 border-t-[var(--accent-blue)] hover:!bg-[var(--bg-card)]">
            <div className="flex items-center gap-3 mb-4">
              <Globe size={28} weight="duotone" className="text-[var(--accent-blue)]" />
              <h3 className="text-lg font-bold text-white">For the Global Economy</h3>
            </div>
            <p className="text-sm leading-relaxed text-[var(--text-secondary)]">
              The Baltic Sea carries 15% of global shipping. Shadow fleet tankers evading sanctions transit the same waters as the submarine cables powering three countries. Every cable attack raises insurance rates, disrupts trade routes, and creates precedent for infrastructure warfare worldwide.
            </p>
          </Section>
        </div>
      </Section>

      {/* ═══ SECTION 4 — WHAT GRIP DOES ═══ */}
      <Section className="py-24 border-t border-[var(--border)]">
        <h2 className="text-3xl md:text-4xl font-black tracking-tight text-center mb-4">
          GRIP monitors what's at risk —<br className="hidden md:inline" /> and what breaks if it fails.
        </h2>
        <p className="text-center text-[var(--text-secondary)] mb-14 text-lg max-w-2xl mx-auto">
          Four integrated analytical capabilities in a single dashboard.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {GRIP_CARDS.map((c, i) => {
            const Icon = c.icon
            return (
              <Section key={i} delay={i * 0.08} className="card p-6 hover:!bg-[var(--bg-card)] group">
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-12 h-12 rounded-lg bg-[var(--bg-primary)] border border-[var(--border-card)] flex items-center justify-center">
                    <Icon size={24} weight="duotone" className="text-[var(--text-primary)]" />
                  </div>
                  <h3 className="text-xl font-bold text-white">{c.title}</h3>
                </div>
                <p className="text-sm leading-relaxed text-[var(--text-secondary)] mb-4">{c.desc}</p>
                <Link
                  to={c.link}
                  className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[var(--accent-blue)] group-hover:text-white transition-colors"
                >
                  Open view <ArrowRight size={14} weight="bold" />
                </Link>
              </Section>
            )
          })}
        </div>
      </Section>

      {/* ═══ SECTION 5 — THE NUMBERS ═══ */}
      <Section className="py-24 border-t border-[var(--border)]">
        <h2 className="text-3xl md:text-4xl font-black tracking-tight text-center mb-4">
          The numbers
        </h2>
        <p className="text-center text-[var(--text-secondary)] mb-14 text-lg max-w-2xl mx-auto">
          Validated results from the GRIP analytical engine.
        </p>

        <div className="overflow-hidden rounded-xl border border-[var(--border-card)]">
          <table className="w-full text-left">
            <thead>
              <tr className="bg-[var(--bg-secondary)] border-b border-[var(--border-card)]">
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-[var(--text-muted)]">Metric</th>
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-[var(--text-muted)]">Value</th>
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-[var(--text-muted)] hidden md:table-cell">What it means</th>
              </tr>
            </thead>
            <tbody>
              {FINDINGS.map((f, i) => (
                <tr key={i} className="border-b border-[var(--border-card)] last:border-0 hover:bg-[var(--bg-card-hover)] transition-colors">
                  <td className="px-6 py-4 font-bold text-sm text-white">{f.metric}</td>
                  <td className="px-6 py-4 font-mono font-bold text-base text-[var(--accent-blue)]">{f.value}</td>
                  <td className="px-6 py-4 text-sm text-[var(--text-secondary)] hidden md:table-cell">{f.meaning}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Section>

      {/* ═══ SECTION 6 — THE CANADA CONNECTION ═══ */}
      <Section className="py-24 border-t border-[var(--border)]">
        <h2 className="text-3xl md:text-4xl font-black tracking-tight text-center mb-4">
          What Canada can do about it
        </h2>
        <div className="max-w-3xl mx-auto text-center mb-14 space-y-4">
          <p className="text-xl text-[var(--text-secondary)] leading-relaxed">
            The Baltics don't need more energy.<br />
            <span className="text-white font-bold">They need more resilience.</span>
          </p>
          <p className="text-base text-[var(--text-muted)]">
            Canada can provide that — through LNG diversification, nuclear fuel-cycle partnership, and exportable intelligence platforms like GRIP.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
          {CANADA_CARDS.map((c, i) => {
            const Icon = c.icon
            return (
              <Section key={i} delay={i * 0.1} className="card p-6 hover:!bg-[var(--bg-card)]">
                <div className="w-12 h-12 rounded-lg bg-[#ef444410] border border-[#ef444430] flex items-center justify-center mb-4">
                  <Icon size={24} weight="duotone" className="text-[var(--score-red)]" />
                </div>
                <h3 className="text-lg font-bold text-white mb-3">{c.title}</h3>
                <p className="text-sm leading-relaxed text-[var(--text-secondary)]">{c.body}</p>
              </Section>
            )
          })}
        </div>

        <div className="text-center">
          <a
            href="https://github.com/gavinshklanka/grip/blob/main/docs/strategic/canada-baltic-opportunity-brief.md"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg border border-[var(--border-card)] bg-[var(--bg-card)] text-sm font-bold text-[var(--text-primary)] hover:border-[var(--accent-blue)] transition-colors"
          >
            <FileText size={18} /> Read the full Canada-Baltic Opportunity Brief
          </a>
        </div>
      </Section>

      {/* ═══ SECTION 7 — WHO BUILT THIS ═══ */}
      <Section className="py-24 border-t border-[var(--border)]">
        <div className="max-w-3xl mx-auto text-center space-y-6">
          <h2 className="text-3xl md:text-4xl font-black tracking-tight">
            Who built this
          </h2>
          <div className="space-y-2">
            <p className="text-2xl font-bold text-white">Gavin Shklanka</p>
            <p className="text-base text-[var(--text-secondary)]">
              MBAN 2026 · Sobey School of Business · Saint Mary's University
            </p>
            <p className="text-base font-bold text-[var(--text-muted)]">Black Point Analytics</p>
          </div>
          <p className="text-sm leading-relaxed text-[var(--text-secondary)] max-w-xl mx-auto pt-4">
            This platform was designed, specified, and built as a portfolio-grade demonstration of applied analytics: data engineering, risk modeling, simulation, visualization, and strategic translation.
          </p>

          <div className="flex items-center justify-center gap-4 pt-8">
            <a
              href="https://github.com/gavinshklanka/grip"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg border border-[var(--border-card)] bg-[var(--bg-card)] text-sm font-bold text-[var(--text-primary)] hover:border-[var(--accent-blue)] transition-colors"
            >
              <GithubLogo size={18} weight="bold" /> GitHub Repository
            </a>
            <Link
              to="/"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-[var(--accent-blue)] text-sm font-bold text-white hover:brightness-110 transition-all"
            >
              Enter the Dashboard <ArrowRight size={16} weight="bold" />
            </Link>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="mt-16 pt-8 border-t border-[var(--border)] mb-8">
          <p className="text-xs text-center text-[var(--text-muted)] italic max-w-2xl mx-auto leading-relaxed">
            GRIP does not predict wars, recommend military actions, or claim operational intelligence capability. It models consequences, dependencies, and fragilities using open-source data with documented methodology.
          </p>
        </div>
      </Section>
    </div>
  )
}
