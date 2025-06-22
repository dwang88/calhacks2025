'use client'

import React from 'react'

interface ErrorBoundaryState {
  hasError: boolean
  error?: Error
}

interface ErrorBoundaryProps {
  children: React.ReactNode
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('🚨🚨🚨 WEBSITE CRASHED! 🚨🚨🚨', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-red-50 flex items-center justify-center p-4">
          <div className="max-w-2xl mx-auto text-center">
            <div className="bg-red-600 text-white p-8 rounded-lg shadow-2xl">
              <div className="text-6xl mb-4">💥</div>
              <h1 className="text-3xl font-bold mb-4">WEBSITE CRASHED!</h1>
              <p className="text-xl mb-6">The distributor system has experienced a critical failure!</p>
              
              <div className="bg-red-700 p-4 rounded mb-6 text-left">
                <p className="font-mono text-sm">
                  ERROR: {this.state.error?.message}
                </p>
              </div>
              
              <div className="space-y-2 text-sm">
                <p>🔥 Database connection: LOST</p>
                <p>⚠️  Distributor network: DOWN</p>
                <p>❌ Emergency protocols: ACTIVATED</p>
              </div>
              
              <button 
                onClick={() => window.location.reload()}
                className="mt-6 bg-white text-red-600 px-6 py-3 rounded-lg font-bold hover:bg-gray-100 transition-colors"
              >
                🔄 Restart System
              </button>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
} 