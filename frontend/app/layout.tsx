import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Website Testing Assistant - AI-Powered Testing Demo',
  description: 'AI-powered website integrity testing with automated test generation, execution, and GitHub issue creation. Built with Next.js, FastAPI, and Claude AI.',
  keywords: ['AI', 'testing', 'automation', 'playwright', 'website', 'quality assurance', 'demo'],
  authors: [{ name: 'CalHacks 2025' }],
  creator: 'CalHacks 2025',
  generator: 'Next.js',
  openGraph: {
    title: 'Website Testing Assistant - AI-Powered Testing Demo',
    description: 'AI-powered website integrity testing with automated test generation and GitHub integration',
    type: 'website',
    locale: 'en_US',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Website Testing Assistant - AI-Powered Testing Demo',
    description: 'AI-powered website integrity testing with automated test generation and GitHub integration',
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className="scroll-smooth">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link 
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" 
          rel="stylesheet" 
        />
        <link rel="icon" href="/favicon.ico" />
      </head>
      <body className="antialiased">
        {children}
      </body>
    </html>
  )
}
