// Volunteer Dashboard Component with live updates
// Place this in: src/components/volunteer/VolunteerDashboard.tsx

'use client';

import { useState, useEffect } from 'react';
import { useDrishtiAPI } from '@/lib/hooks/useDrishtiAPI';
import { useVolunteerWebSocket } from '@/lib/hooks/useWebSocket';

interface Dispatch {
  id: string;
  type: string;
  description: string;
  location: {
    lat: number;
    lng: number;
  };
  priority: 'low' | 'medium' | 'high';
  created_at: string;
  status: 'pending' | 'acknowledged' | 'en_route' | 'completed';
}

interface VolunteerDashboardProps {
  volunteerId: string;
  volunteerName: string;
}

export default function VolunteerDashboard({
  volunteerId,
  volunteerName,
}: VolunteerDashboardProps) {
  const [dispatches, setDispatches] = useState<Dispatch[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [location, setLocation] = useState<{ lat: number; lng: number } | null>(null);

  const { acknowledgeDispatch, getVolunteerDispatches, error } = useDrishtiAPI();

  const { sendMessage, isConnected, lastMessage } = useVolunteerWebSocket(
    volunteerId,
    {
      onMessage: (data) => {
        console.log('Received message:', data);
        
        if (data.type === 'new_dispatch') {
          setDispatches(prev => [data.data, ...prev]);
        } else if (data.type === 'new_sos') {
          setAlerts(prev => [data.data, ...prev]);
        } else if (data.type === 'high_risk_detected') {
          setAlerts(prev => [data.data, ...prev]);
        }
      },
    }
  );

  // Load initial dispatches
  useEffect(() => {
    const loadDispatches = async () => {
      try {
        const result = await getVolunteerDispatches(volunteerId) as { dispatches: Dispatch[] };
        setDispatches(result.dispatches || []);
      } catch (err) {
        console.error('Failed to load dispatches:', err);
      }
    };

    loadDispatches();
  }, [volunteerId, getVolunteerDispatches]);

  // Get current location
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const currentLocation = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          };
          setLocation(currentLocation);
          
          // Send location update
          if (isConnected) {
            sendMessage({
              type: 'location_update',
              location: currentLocation,
            });
          }
        },
        (error) => {
          console.error('Failed to get location:', error);
        }
      );
    }
  }, [isConnected, sendMessage]);

  const handleAcknowledgeDispatch = async (dispatch: Dispatch) => {
    try {
      await acknowledgeDispatch({
        dispatch_id: dispatch.id,
        volunteer_id: volunteerId,
        status: 'acknowledged',
        location: location || undefined,
      });

      // Update local state
      setDispatches(prev =>
        prev.map(d =>
          d.id === dispatch.id ? { ...d, status: 'acknowledged' } : d
        )
      );
    } catch (err) {
      console.error('Failed to acknowledge dispatch:', err);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'border-red-500 bg-red-900/20';
      case 'medium':
        return 'border-yellow-500 bg-yellow-900/20';
      case 'low':
        return 'border-blue-500 bg-blue-900/20';
      default:
        return 'border-gray-500 bg-gray-900/20';
    }
  };

  const getTimeAgo = (timestamp: string) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffMs = now.getTime() - time.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} mins ago`;
    
    const diffHours = Math.floor(diffMins / 60);
    return `${diffHours} hours ago`;
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 p-4">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-blue-400">Drishti</h1>
          </div>
          <div className="flex items-center space-x-4">
            <span>Hi, {volunteerName}</span>
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
              {volunteerName.charAt(0).toUpperCase()}
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Volunteer Live Feed</h1>

        {/* Connection Status */}
        <div className="mb-6 flex items-center space-x-2">
          <div
            className={`w-3 h-3 rounded-full ${
              isConnected ? 'bg-green-400' : 'bg-red-400'
            }`}
          />
          <span className="text-sm text-gray-400">
            {isConnected ? 'Connected to live feed' : 'Disconnected'}
          </span>
        </div>

        {/* My Dispatches Section */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">My Dispatches</h2>
          <p className="text-gray-400 mb-6">
            Tasks and locations assigned directly to you. Acknowledge and proceed to the location.
          </p>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {dispatches.map((dispatch) => (
              <div
                key={dispatch.id}
                className={`p-6 rounded-lg border-2 ${getPriorityColor(
                  dispatch.priority
                )}`}
              >
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-xl font-semibold">{dispatch.type}</h3>
                  <div className="flex items-center space-x-2">
                    <span
                      className={`px-2 py-1 rounded text-xs font-medium ${
                        dispatch.priority === 'high'
                          ? 'bg-red-500 text-white'
                          : dispatch.priority === 'medium'
                          ? 'bg-yellow-500 text-black'
                          : 'bg-blue-500 text-white'
                      }`}
                    >
                      {dispatch.priority.toUpperCase()}
                    </span>
                    <span className="bg-blue-500 text-white px-2 py-1 rounded text-xs">
                      Dispatch
                    </span>
                  </div>
                </div>

                <div className="flex items-center text-gray-400 text-sm mb-4">
                  <span>🕒</span>
                  <span className="ml-1">{getTimeAgo(dispatch.created_at)}</span>
                </div>

                <p className="text-gray-300 mb-4">{dispatch.description}</p>

                <div className="flex items-center text-blue-400 mb-4">
                  <span>📍</span>
                  <span className="ml-1">
                    Zone at {dispatch.location.lat.toFixed(4)}, {dispatch.location.lng.toFixed(4)}
                  </span>
                </div>

                {dispatch.status === 'pending' && (
                  <button
                    onClick={() => handleAcknowledgeDispatch(dispatch)}
                    className="w-full bg-blue-500 hover:bg-blue-600 text-white py-3 rounded-lg font-medium transition-colors"
                  >
                    Acknowledge
                  </button>
                )}

                {dispatch.status === 'acknowledged' && (
                  <div className="w-full bg-green-500/20 border border-green-500 text-green-400 py-3 rounded-lg text-center font-medium">
                    Acknowledged
                  </div>
                )}
              </div>
            ))}

            {dispatches.length === 0 && (
              <div className="col-span-2 text-center py-12 text-gray-400">
                <p>No dispatches assigned to you at the moment.</p>
              </div>
            )}
          </div>
        </section>

        {/* Live Anomaly Alerts */}
        <section>
          <h2 className="text-2xl font-semibold mb-4">Live Anomaly Alerts</h2>
          <p className="text-gray-400 mb-6">
            General event-wide alerts for situational awareness.
          </p>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {alerts.map((alert, index) => (
              <div
                key={index}
                className={`p-6 rounded-lg border-2 ${
                  alert.type === 'new_sos'
                    ? 'border-red-500 bg-red-900/20'
                    : 'border-yellow-500 bg-yellow-900/20'
                }`}
              >
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-xl font-semibold">
                    {alert.type === 'new_sos' ? 'SOS Beacon Activated' : 'Overcrowding Detected'}
                  </h3>
                  <span
                    className={`px-2 py-1 rounded text-xs font-medium ${
                      alert.type === 'new_sos'
                        ? 'bg-red-500 text-white'
                        : 'bg-yellow-500 text-black'
                    }`}
                  >
                    {alert.type === 'new_sos' ? 'SOS' : 'Anomaly'}
                  </span>
                </div>

                <div className="flex items-center text-gray-400 text-sm mb-4">
                  <span>🕒</span>
                  <span className="ml-1">{getTimeAgo(alert.timestamp)}</span>
                </div>

                <p className="text-gray-300 mb-4">
                  {alert.type === 'new_sos'
                    ? 'An attendee has activated their SOS beacon. A dispatch has been sent to the nearest volunteer.'
                    : 'Unusual crowd density forming at the main stage east entrance. Monitor the situation.'}
                </p>

                <div className="flex items-center text-blue-400">
                  <span>📍</span>
                  <span className="ml-1">
                    {alert.location
                      ? `${alert.location.lat?.toFixed(4)}, ${alert.location.lng?.toFixed(4)}`
                      : 'Main Stage, East Entrance'}
                  </span>
                </div>
              </div>
            ))}

            {alerts.length === 0 && (
              <div className="col-span-2 text-center py-12 text-gray-400">
                <p>No alerts at the moment. All systems normal.</p>
              </div>
            )}
          </div>
        </section>

        {/* Error Display */}
        {error && (
          <div className="fixed bottom-4 right-4 bg-red-900 border border-red-500 text-red-300 p-4 rounded-lg max-w-sm">
            <p className="text-sm">{error}</p>
          </div>
        )}
      </div>
    </div>
  );
}
