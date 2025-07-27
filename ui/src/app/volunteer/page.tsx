
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Header } from '@/components/header';
import { Footer } from '@/components/footer';
import { AlertCard, type AlertProps } from '@/components/volunteer/alert-card';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { useToast } from '@/hooks/use-toast';
import { useDrishtiAPI } from '@/lib/hooks/useDrishtiAPI';


interface User {
  name: string;
}

const myDispatchesData: AlertProps[] = [
  {
    type: 'Dispatch',
    title: 'Assist Attendee',
    time: '2 mins ago',
    description: 'Medical assistance needed near the food court for a person feeling faint.',
    location: 'Zone B, Food Court',
    showAcknowledge: true,
  },
  {
    type: 'Dispatch',
    title: 'Investigate Disturbance',
    time: '8 mins ago',
    description: 'Reports of a minor argument. Your presence is requested to de-escalate.',
    location: 'Zone A, Merch Tent',
    showAcknowledge: true,
  },
];

// Default data - fallback when CNS data is not available
const defaultLiveAnomalies: AlertProps[] = [
    {
        type: 'Anomaly',
        title: 'Overcrowding Detected',
        time: '5 mins ago',
        description: 'Unusual crowd density forming at the main stage east entrance. Monitor the situation.',
        location: 'Main Stage, East Entrance',
    },
    {
        type: 'SOS',
        title: 'SOS Beacon Activated',
        time: '12 mins ago',
        description: 'An attendee has activated their SOS beacon. A dispatch has been sent to the nearest volunteer.',
        location: 'Zone D, near Restroom 3',
    },
];

const defaultCrowdInsights: AlertProps[] = [
    {
        type: 'CNS',
        title: 'Weather Alert: Heavy Rain',
        time: '10 mins ago',
        description: 'Heavy rainfall expected in 30 minutes. Advise attendees to seek shelter. Tents are located in Zones A and C.',
        location: 'All Zones',
    },
    {
        type: 'CNS',
        title: 'High Traffic Prediction',
        time: 'Now',
        description: 'AI predicts a surge in foot traffic towards the north exit in the next 15 minutes as the current act finishes. Prepare for crowd management.',
        location: 'North Exit, Zone A',
    },
    {
        type: 'CNS',
        title: 'Potential Bottleneck',
        time: 'Prediction for 8:30 PM',
        description: 'The path between the secondary stage and food court is likely to become congested. Recommend proactive rerouting of foot traffic.',
        location: 'Pathway B-C',
    },
];

export default function VolunteerPage() {
    const [user, setUser] = useState<User | null>(null);
    const router = useRouter();
    const [isAlertOpen, setIsAlertOpen] = useState(false);
    const [selectedAlert, setSelectedAlert] = useState<AlertProps | null>(null);
    const { toast } = useToast();
    const [acknowledgedDispatches, setAcknowledgedDispatches] = useState<string[]>([]);
    const [myDispatches, setMyDispatches] = useState<AlertProps[]>(myDispatchesData);
    
    // CNS Integration State
    const [liveAnomalies, setLiveAnomalies] = useState<AlertProps[]>([]);
    const [crowdInsights, setCrowdInsights] = useState<AlertProps[]>([]);
    const [isLoadingCNSData, setIsLoadingCNSData] = useState(false);
    const [cnsDataError, setCnsDataError] = useState<string | null>(null);
    
    // API Hook
    const { 
        getCrowdSafetyInsights, 
        getLiveAnomalyAlerts, 
        startCNSAnalysis,
        isConnected,
        error 
    } = useDrishtiAPI();


    useEffect(() => {
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
        const parsedUser = JSON.parse(storedUser);
        if (parsedUser.role === 'volunteer') {
            setUser(parsedUser);
        } else {
            router.push('/login');
        }
        } else {
        router.push('/login');
        }
    }, [router]);

    // Load CNS data on component mount and set up polling
    useEffect(() => {
        if (user) {
            loadCNSData();
            
            // Poll for updates every 30 seconds
            const interval = setInterval(loadCNSData, 30000);
            return () => clearInterval(interval);
        }
    }, [user]);

    const loadCNSData = async () => {
        if (isLoadingCNSData) return; // Prevent multiple concurrent requests
        
        setIsLoadingCNSData(true);
        setCnsDataError(null);
        
        try {
            // Load both anomaly alerts and crowd insights
            const [anomalyResponse, insightsResponse] = await Promise.all([
                getLiveAnomalyAlerts(),
                getCrowdSafetyInsights()
            ]);

            // Process anomaly alerts
            if ((anomalyResponse as any)?.success && (anomalyResponse as any)?.alerts) {
                const formattedAlerts: AlertProps[] = (anomalyResponse as any).alerts.map((alert: any) => ({
                    type: alert.type,
                    title: alert.title,
                    time: alert.time,
                    description: alert.description,
                    location: alert.location,
                }));
                setLiveAnomalies(formattedAlerts);
            }

            // Process crowd insights
            if ((insightsResponse as any)?.success && (insightsResponse as any)?.insights) {
                const formattedInsights: AlertProps[] = (insightsResponse as any).insights.map((insight: any) => ({
                    type: insight.type,
                    title: insight.title,
                    time: insight.time,
                    description: insight.description,
                    location: insight.location,
                }));
                setCrowdInsights(formattedInsights);
            }

            console.log('CNS data loaded successfully');
            
        } catch (err) {
            console.error('Failed to load CNS data:', err);
            setCnsDataError('Failed to load live data. Using cached information.');
            
            // Fallback to default data if API fails
            if (liveAnomalies.length === 0) {
                setLiveAnomalies(defaultLiveAnomalies);
            }
            if (crowdInsights.length === 0) {
                setCrowdInsights(defaultCrowdInsights);
            }
            
        } finally {
            setIsLoadingCNSData(false);
        }
    };

    const startAnalysis = async () => {
        try {
            setIsLoadingCNSData(true);
            toast({
                title: 'Starting Analysis',
                description: 'CNS analysis is being initiated...',
            });

            // Start CNS analysis (this will trigger the IP camera analysis)
            const response = await startCNSAnalysis();
            
            if ((response as any)?.success) {
                toast({
                    title: 'Analysis Started',
                    description: 'CNS analysis has started successfully. Live data will be updated.',
                });
                
                // Load fresh data after starting analysis
                setTimeout(loadCNSData, 2000);
            }
            
        } catch (err) {
            console.error('Failed to start analysis:', err);
            toast({
                variant: 'destructive',
                title: 'Analysis Failed',
                description: 'Failed to start CNS analysis. Please try again.',
            });
        } finally {
            setIsLoadingCNSData(false);
        }
    };

    const handleAcknowledgeClick = (alert: AlertProps) => {
        setSelectedAlert(alert);
        setIsAlertOpen(true);
    };

    const handleAcknowledgeSubmit = () => {
        setIsAlertOpen(false);
        if (!navigator.geolocation) {
            toast({
                variant: 'destructive',
                title: 'Geolocation Not Supported',
                description: 'Your browser does not support geolocation.',
            });
            return;
        }

        toast({
            title: 'Sending Location...',
            description: 'Please wait while we confirm your position.',
        });

        navigator.geolocation.getCurrentPosition(
            (position) => {
                const { latitude, longitude } = position.coords;
                // Simulate sending data to backend
                console.log('Dispatch Acknowledged at location:', {
                    alert: selectedAlert?.title,
                    location: { latitude, longitude },
                });
                toast({
                    title: 'Dispatch Acknowledged',
                    description: `You have confirmed arrival for: ${selectedAlert?.title}. Your location has been recorded.`,
                });
                if (selectedAlert) {
                  setAcknowledgedDispatches(prev => [...prev, selectedAlert.title]);
                }
            },
            (error) => {
                toast({
                    variant: 'destructive',
                    title: 'Location Access Denied',
                    description: 'Please enable location services to acknowledge the dispatch.',
                });
            }
        );
    };


    if (!user) {
        return (
          <div className="min-h-screen flex items-center justify-center bg-background">
            <p>Loading...</p>
          </div>
        );
    }

  return (
    <>
      <div className="min-h-screen flex flex-col bg-background">
        <Header userName={user.name} />
        <main className="flex-grow container mx-auto p-4 md:p-6 md:py-12 text-foreground rounded-t-lg">
          <div className="flex justify-between items-center mb-8">
            <h1 className="font-headline text-3xl md:text-4xl font-bold text-foreground">Volunteer Live Feed</h1>
            
            {/* CNS Controls */}
            <div className="flex items-center space-x-4">
              {/* Connection Status */}
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`} />
                <span className="text-sm text-muted-foreground">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              
              {/* Start Analysis Button */}
              <button
                onClick={startAnalysis}
                disabled={isLoadingCNSData}
                className="bg-blue-500 hover:bg-blue-600 disabled:bg-blue-300 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              >
                {isLoadingCNSData ? 'Starting...' : 'Start Analysis'}
              </button>
            </div>
          </div>
          
          {/* Error Display */}
          {(error || cnsDataError) && (
            <div className="mb-6 p-4 bg-red-900/20 border border-red-500 text-red-300 rounded-lg">
              <p className="text-sm">{error || cnsDataError}</p>
            </div>
          )}
          
          {/* Loading Indicator */}
          {isLoadingCNSData && (
            <div className="mb-6 p-4 bg-blue-900/20 border border-blue-500 text-blue-300 rounded-lg">
              <p className="text-sm">Loading live CNS data...</p>
            </div>
          )}
          
          <div className="flex flex-col gap-12">
            {/* My Dispatches Section */}
            <div>
              <h2 className="font-headline text-2xl font-bold mb-2 text-foreground">My Dispatches</h2>
              <p className="text-muted-foreground mb-6">Tasks and locations assigned directly to you. Acknowledge and proceed to the location.</p>
              <div className="grid gap-6 md:grid-cols-2">
                {myDispatches.map((alert, index) => (
                  <AlertCard 
                    key={`dispatch-${index}`} 
                    onAcknowledge={() => handleAcknowledgeClick(alert)} 
                    isAcknowledged={acknowledgedDispatches.includes(alert.title)}
                    {...alert} 
                  />
                ))}
              </div>
            </div>

            {/* Live Anomaly Alerts Section */}
            <div>
              <h2 className="font-headline text-2xl font-bold mb-2 text-foreground">Live Anomaly Alerts</h2>
              <p className="text-muted-foreground mb-6">General event-wide alerts for situational awareness.</p>
              <div className="grid gap-6 md:grid-cols-2">
                {liveAnomalies.map((alert, index) => (
                  <AlertCard key={`anomaly-${index}`} {...alert} />
                ))}
              </div>
            </div>

            {/* Crowd & Safety Insights Section */}
            <div>
              <h2 className="font-headline text-2xl font-bold mb-2 text-foreground">Crowd & Safety Insights</h2>
              <p className="text-muted-foreground mb-6">AI-powered predictions and event-wide notices from Central Command.</p>
              <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
                {crowdInsights.map((alert, index) => (
                  <AlertCard key={`cns-${index}`} {...alert} />
                ))}
              </div>
            </div>
          </div>
        </main>
        <Footer />
      </div>

      <AlertDialog open={isAlertOpen} onOpenChange={setIsAlertOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="font-headline">Confirm Your Arrival</AlertDialogTitle>
            <AlertDialogDescription>
              This action will send your current location to confirm you have reached the destination for: &quot;{selectedAlert?.title}&quot;.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleAcknowledgeSubmit}>Send Location & Submit</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
