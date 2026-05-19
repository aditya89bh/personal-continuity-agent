import './globals.css'

export const metadata = {
  title: 'Personal Continuity Agent',
  description: 'A continuity-aware memory interface for long-horizon AI systems.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
