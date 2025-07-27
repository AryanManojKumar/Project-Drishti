// Example SOS Component using the API
// Place this in: src/components/sos/SOSButton.tsx

'use client';

import { useState } from 'react';
import { useDrishtiAPI } from '@/lib/hooks/useDrishtiAPI';
import { useAttendeeWebSocket } from '@/lib/hooks/useWebSocket';

interface SOSButtonProps {
  userId: string;
  className?: string;
}

export default function SOSButton({ userId, className = '' }: SOSButtonProps) {
  const [isActivating, setIsActivating] = useState(false);
  const [isActive, setIsActive] = useState(false);
  const [location, setLocation] = useState<{ lat: number; lng: number } | null>(null);
  
  const { createSOS, error, clearError } = useDrishtiAPI();
  
  const { sendMessage, isConnected } = useAttendeeWebSocket(userId, {
    onMessage: (data) => {
      if (data.type === 'sos_response') {
        setIsActive(true);
        setIsActivating(false);
      }
    }
  });

  const getCurrentLocation = (): Promise<{ lat: number; lng: number }> => {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation is not supported'));
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          });
        },
        (error) => {
          reject(error);
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 60000,
        }
      );
    });
  };

  const handleSOSClick = async () => {
    if (isActivating || isActive) return;

    setIsActivating(true);
    clearError();

    try {
      // Get current location
      const currentLocation = await getCurrentLocation();
      setLocation(currentLocation);

      // Create SOS request
      const sosRequest = {
        user_id: userId,
        location: currentLocation,
        emergency_type: 'general',
        timestamp: new Date().toISOString(),
      };

      // Send via REST API
      await createSOS(sosRequest);

      // Also send via WebSocket for real-time updates
      if (isConnected) {
        sendMessage({
          type: 'emergency_sos',
          location: currentLocation,
          emergency_type: 'general',
        });
      }

      setIsActive(true);
    } catch (err) {
      console.error('Failed to activate SOS:', err);
    } finally {
      setIsActivating(false);
    }
  };

  return (
    <div className={`flex flex-col items-center space-y-4 ${className}`}>
      {/* SOS Button */}
      <button
        onClick={handleSOSClick}
        disabled={isActivating || isActive}
        className={`
          w-64 h-64 rounded-full border-4 flex items-center justify-center
          transition-all duration-300 transform hover:scale-105
          ${
            isActive
              ? 'bg-green-500 border-green-400 animate-pulse'
              : isActivating
              ? 'bg-orange-500 border-orange-400 animate-spin'
              : 'bg-red-500 border-red-400 hover:bg-red-600'
          }
        `}
      >
        <div className="text-center">
          <div className="text-white text-2xl mb-2">
            {isActive ? '✓' : isActivating ? '...' : '🏠'}
          </div>
          <div className="text-white text-xl font-bold">
            {isActive ? 'Alert Sent' : isActivating ? 'Sending...' : 'SOS'}
          </div>
          {isActive && (
            <div className="text-white text-sm mt-1">
              Help is on the way.
            </div>
          )}
        </div>
      </button>

      {/* Status Message */}
      {isActive && location && (
        <div className="bg-gray-800 rounded-lg p-4 text-center max-w-md">
          <h3 className="text-white font-semibold mb-2">SOS Alert Sent</h3>
          <p className="text-gray-300 text-sm">
            Help is on the way. A volunteer has been notified.
          </p>
          <div className="text-gray-400 text-xs mt-2">
            Location: {location.lat.toFixed(6)}, {location.lng.toFixed(6)}
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="bg-red-900 rounded-lg p-4 text-center max-w-md">
          <p className="text-red-300 text-sm">{error}</p>
          <button
            onClick={clearError}
            className="text-red-400 underline text-xs mt-1"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Connection Status */}
      <div className="flex items-center space-x-2 text-sm">
        <div
          className={`w-2 h-2 rounded-full ${
            isConnected ? 'bg-green-400' : 'bg-red-400'
          }`}
        />
        <span className="text-gray-400">
          {isConnected ? 'Connected' : 'Disconnected'}
        </span>
      </div>
    </div>
  );
}
