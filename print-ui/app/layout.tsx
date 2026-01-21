import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Label Print Station | Alliance Chemical',
  description: 'Print product labels for Alliance Chemical',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gray-50">
          {/* Header */}
          <header className="bg-alliance-charcoal text-white shadow-lg">
            <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <h1 className="text-xl font-bold">Label Print Station</h1>
                <span className="text-gray-400 text-sm">Alliance Chemical</span>
              </div>
              <nav className="flex items-center gap-6">
                <a href="/" className="hover:text-alliance-purple transition-colors">
                  Print
                </a>
                <a href="/history" className="hover:text-alliance-purple transition-colors">
                  History
                </a>
              </nav>
            </div>
          </header>

          {/* Main content */}
          <main className="max-w-7xl mx-auto px-4 py-8">
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}
