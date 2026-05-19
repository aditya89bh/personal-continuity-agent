"use client"

import { useEffect, useMemo, useState } from "react"

type TimelineEvent = {
  event_id?: string
  event_type?: string
  type?: string
  content: string
  tags?: string[]
  importance?: number
  salience: number
}

type TimelineDay = {
  date: string
  events: TimelineEvent[]
}

type ReflectionResponse = {
  summary: string
  recommendations: string[]
  momentum_status?: string
  continuity_gaps?: number
}

const fallbackTimeline: TimelineDay[] = [
  {
    date: "2026-01-01",
    events: [
      {
        type: "goal",
        content: "User commits to building a continuity-aware AI architecture.",
        salience: 0.92,
      },
      {
        type: "progress",
        content: "User implements identity modeling and reflection systems.",
        salience: 0.84,
      },
    ],
  },
  {
    date: "2026-03-14",
    events: [
      {
        type: "contradiction",
        content: "User abandons continuity writing for several weeks.",
        salience: 0.88,
      },
    ],
  },
  {
    date: "2026-04-02",
    events: [
      {
        type: "repair_action",
        content: "User resumes continuity research and publishes new architecture notes.",
        salience: 0.9,
      },
    ],
  },
]

const identityThemes = [
  "Continuity Research",
  "Cognitive Architectures",
  "Identity Modeling",
  "Temporal Intelligence",
]

const fallbackReflection: ReflectionResponse = {
  summary:
    "The system detects recurring continuity themes around identity, memory systems, and long-horizon AI architectures. A temporary contradiction period was later repaired through renewed research activity.",
  recommendations: ["Keep reinforcing high-salience continuity behaviors."],
  momentum_status: "strong_momentum",
  continuity_gaps: 1,
}

export default function HomePage() {
  const [timeline, setTimeline] = useState<TimelineDay[]>(fallbackTimeline)
  const [reflection, setReflection] = useState<ReflectionResponse>(fallbackReflection)
  const [dataMode, setDataMode] = useState<"live" | "demo">("demo")

  useEffect(() => {
    async function loadContinuityData() {
      try {
        const [timelineResponse, reflectionResponse] = await Promise.all([
          fetch("http://127.0.0.1:8000/timeline"),
          fetch("http://127.0.0.1:8000/reflection"),
        ])

        if (!timelineResponse.ok || !reflectionResponse.ok) {
          throw new Error("API unavailable")
        }

        const timelineData = await timelineResponse.json()
        const reflectionData = await reflectionResponse.json()

        if (Array.isArray(timelineData) && timelineData.length > 0) {
          setTimeline(timelineData)
        }

        setReflection(reflectionData)
        setDataMode("live")
      } catch {
        setDataMode("demo")
      }
    }

    loadContinuityData()
  }, [])

  const eventCount = useMemo(
    () => timeline.reduce((count, day) => count + day.events.length, 0),
    [timeline],
  )

  const momentumLabel = reflection.momentum_status
    ? reflection.momentum_status.replaceAll("_", " ")
    : "strong"

  return (
    <main className="page-shell">
      <section className="hero">
        <p className="eyebrow">Personal Continuity Agent</p>
        <h1>A continuity-aware memory interface for long-horizon AI systems.</h1>
        <p className="hero-copy">
          This interface explores how intelligent systems might visualize identity
          evolution, continuity gaps, memory salience, contradiction repair, and
          temporal reflection over long periods of time.
        </p>
      </section>

      <section className="dashboard-grid">
        <div className="panel timeline-panel">
          <div className="panel-header">
            <div>
              <h2>Continuity Timeline</h2>
              <p>Salience-ranked continuity events across time.</p>
            </div>
            <span className="count-pill">{eventCount} memory events · {dataMode}</span>
          </div>

          <div className="timeline-list">
            {timeline.map((day) => (
              <div className="timeline-day" key={day.date}>
                <div className="timeline-date">{day.date}</div>

                <div className="event-stack">
                  {day.events.map((event, index) => {
                    const eventType = event.event_type || event.type || "note"
                    return (
                      <article className="event-card" key={event.event_id || `${day.date}-${index}`}>
                        <div className="event-meta">
                          <span className={`event-type ${eventType}`}>{eventType}</span>
                          <span className="salience">salience {event.salience}</span>
                        </div>
                        <p>{event.content}</p>
                      </article>
                    )
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>

        <aside className="side-stack">
          <div className="panel insight-panel">
            <p className="panel-label">Reflection Summary</p>
            <h3>Continuity state generated from {dataMode} memory.</h3>
            <p>{reflection.summary}</p>
          </div>

          <div className="panel">
            <p className="panel-label">Identity Themes</p>
            <div className="theme-wrap">
              {identityThemes.map((theme) => (
                <span className="theme-chip" key={theme}>{theme}</span>
              ))}
            </div>
          </div>

          <div className="panel">
            <p className="panel-label">Continuity State</p>
            <div className="state-list">
              <div><span>Momentum</span><strong className="positive">{momentumLabel}</strong></div>
              <div><span>Continuity Gaps</span><strong>{reflection.continuity_gaps ?? 0}</strong></div>
              <div><span>Data Source</span><strong>{dataMode}</strong></div>
            </div>
          </div>
        </aside>
      </section>
    </main>
  )
}
