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

export default function HomePage() {
  return (
    <main className="min-h-screen bg-black text-white px-8 py-10">
      <div className="max-w-6xl mx-auto">
        <div className="mb-10">
          <p className="uppercase tracking-[0.3em] text-sm text-zinc-500 mb-3">
            Personal Continuity Agent
          </p>

          <h1 className="text-5xl font-semibold leading-tight max-w-4xl">
            A continuity-aware memory interface for long-horizon AI systems.
          </h1>

          <p className="mt-6 text-zinc-400 max-w-3xl text-lg leading-relaxed">
            This interface explores how intelligent systems might visualize
            identity evolution, continuity gaps, memory salience, contradiction
            repair, and temporal reflection over long periods of time.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <section className="lg:col-span-2 rounded-3xl border border-zinc-800 bg-zinc-950 p-6">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="text-2xl font-medium">Continuity Timeline</h2>
                <p className="text-zinc-500 mt-1">
                  Salience-ranked continuity events across time.
                </p>
              </div>

              <div className="text-sm text-zinc-500">
                5 memory events
              </div>
            </div>

            <div className="space-y-10">
              {mockTimeline.map((day) => (
                <div key={day.date}>
                  <div className="mb-4 text-zinc-500 text-sm tracking-wide">
                    {day.date}
                  </div>

                  <div className="space-y-4 border-l border-zinc-800 pl-6 ml-2">
                    {day.events.map((event, index) => (
                      <div
                        key={index}
                        className="rounded-2xl border border-zinc-800 bg-zinc-900 p-5"
                      >
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <span className="text-xs uppercase tracking-wide px-3 py-1 rounded-full border border-zinc-700 text-zinc-400">
                              {event.type}
                            </span>
                          </div>

                          <div className="text-sm text-zinc-500">
                            salience {event.salience}
                          </div>
                        </div>

                        <p className="text-zinc-200 leading-relaxed text-lg">
                          {event.content}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section className="space-y-6">
            <div className="rounded-3xl border border-zinc-800 bg-zinc-950 p-6">
              <p className="text-zinc-500 text-sm uppercase tracking-wide mb-3">
                Reflection Summary
              </p>

              <h3 className="text-2xl font-medium leading-snug mb-4">
                Identity momentum remains strong despite continuity interruptions.
              </h3>

              <p className="text-zinc-400 leading-relaxed">
                The system detects recurring continuity themes around identity,
                memory systems, and long-horizon AI architectures. A temporary
                contradiction period was later repaired through renewed research
                activity.
              </p>
            </div>

            <div className="rounded-3xl border border-zinc-800 bg-zinc-950 p-6">
              <p className="text-zinc-500 text-sm uppercase tracking-wide mb-5">
                Identity Themes
              </p>

              <div className="flex flex-wrap gap-3">
                {[
                  "Continuity Research",
                  "Cognitive Architectures",
                  "Identity Modeling",
                  "Temporal Intelligence",
                ].map((theme) => (
                  <div
                    key={theme}
                    className="px-4 py-2 rounded-full border border-zinc-700 text-zinc-300"
                  >
                    {theme}
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-3xl border border-zinc-800 bg-zinc-950 p-6">
              <p className="text-zinc-500 text-sm uppercase tracking-wide mb-4">
                Continuity State
              </p>

              <div className="space-y-4 text-zinc-300">
                <div className="flex items-center justify-between">
                  <span>Momentum</span>
                  <span className="text-emerald-400">Strong</span>
                </div>

                <div className="flex items-center justify-between">
                  <span>Continuity Gaps</span>
                  <span>1</span>
                </div>

                <div className="flex items-center justify-between">
                  <span>Repair Rate</span>
                  <span>100%</span>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </main>
  )
}
