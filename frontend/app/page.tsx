const mockTimeline = [
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

export default function HomePage() {
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
            <span className="count-pill">5 memory events</span>
          </div>

          <div className="timeline-list">
            {mockTimeline.map((day) => (
              <div className="timeline-day" key={day.date}>
                <div className="timeline-date">{day.date}</div>

                <div className="event-stack">
                  {day.events.map((event, index) => (
                    <article className="event-card" key={index}>
                      <div className="event-meta">
                        <span className={`event-type ${event.type}`}>{event.type}</span>
                        <span className="salience">salience {event.salience}</span>
                      </div>
                      <p>{event.content}</p>
                    </article>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        <aside className="side-stack">
          <div className="panel insight-panel">
            <p className="panel-label">Reflection Summary</p>
            <h3>Identity momentum remains strong despite continuity interruptions.</h3>
            <p>
              The system detects recurring continuity themes around identity,
              memory systems, and long-horizon AI architectures. A temporary
              contradiction period was later repaired through renewed research
              activity.
            </p>
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
              <div><span>Momentum</span><strong className="positive">Strong</strong></div>
              <div><span>Continuity Gaps</span><strong>1</strong></div>
              <div><span>Repair Rate</span><strong>100%</strong></div>
            </div>
          </div>
        </aside>
      </section>
    </main>
  )
}
