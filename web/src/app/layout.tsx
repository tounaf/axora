import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Axora - Assistant Dédié Métier',
  description: 'From intent to action. Conversational AI Data Platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fr" className="h-full">
      <body className="h-full flex overflow-hidden font-sans text-slate-800 bg-[#f8fafc] antialiased">
        {children}
      </body>
    </html>
  )
}
