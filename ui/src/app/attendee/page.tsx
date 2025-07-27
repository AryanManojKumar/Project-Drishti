'use client'

import { useState } from 'react'
import Link from 'next/link'
import { CheckCircle } from 'lucide-react'

export default function AttendeeDashboard() {
  const [sosActivated, setSosActivated] = useState(false)
  const [showNotification, setShowNotification] = useState(false)

  const handleSOSClick = () => {
    setSosActivated(true)
    setShowNotification(true)
    // Hide notification after 5 seconds
    setTimeout(() => setShowNotification(false), 5000)
  }

  return (
    <div className="min-h-screen bg-slate-900 relative">
      {/* Navigation */}
      <nav className="flex justify-between items-center p-6 border-b border-slate-700">
        <Link href="/" className="text-2xl font-bold text-blue-400">
          Drishti
        </Link>
        <div className="flex items-center gap-4">
          <span className="text-gray-300">Hi, Alex</span>
          <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
            <span className="text-white font-semibold">A</span>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="flex flex-col items-center justify-center min-h-[calc(100vh-100px)] px-6">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-4">
            Emergency Assistance
          </h1>
          <p className="text-xl text-gray-300 max-w-2xl">
            In case of a critical emergency, press the button below.
          </p>
          <p className="text-lg text-gray-400 mt-2">
            Your location will be shared with the nearest volunteer.
          </p>
        </div>

        {/* SOS Button */}
        <div className="mb-8">
          {!sosActivated ? (
            <button
              onClick={handleSOSClick}
              className="w-80 h-80 bg-red-500 hover:bg-red-600 rounded-full flex flex-col items-center justify-center text-white transition-all duration-200 transform hover:scale-105 shadow-2xl"
            >
              <div className="text-xl mb-2">🚨</div>
              <div className="text-4xl font-bold">SOS</div>
            </button>
          ) : (
            <div className="w-80 h-80 bg-green-600 rounded-full flex flex-col items-center justify-center text-white shadow-2xl">
              <CheckCircle size={60} className="mb-4" />
              <div className="text-2xl font-bold mb-2">Alert Sent</div>
              <div className="text-lg">Help is on the way.</div>
            </div>
          )}
        </div>
      </div>

      {/* Notification Toast */}
      {showNotification && (
        <div className="fixed bottom-6 right-6 bg-green-600 text-white p-4 rounded-lg shadow-lg max-w-sm animate-slide-in">
          <div className="flex items-start gap-3">
            <CheckCircle size={24} className="mt-1 flex-shrink-0" />
            <div>
              <div className="font-semibold">SOS Alert Sent</div>
              <div className="text-sm opacity-90">
                Help is on the way. A volunteer has been notified.
              </div>
            </div>
            <button
              onClick={() => setShowNotification(false)}
              className="text-white hover:text-gray-200 ml-2"
            >
              ×
            </button>
          </div>
        </div>
      )}

      <style jsx>{`
        @keyframes slide-in {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
        .animate-slide-in {
          animation: slide-in 0.3s ease-out;
        }
      `}</style>
    </div>
  )
}
