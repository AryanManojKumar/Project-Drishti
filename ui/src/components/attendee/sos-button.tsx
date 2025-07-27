"use client";

import { useState } from 'react';
import { Siren, Loader2, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { useToast } from '@/hooks/use-toast';

export function SosButton() {
  const [status, setStatus] = useState<'idle' | 'loading' | 'sent'>('idle');
  const { toast } = useToast();

  const handleSendSos = () => {
    setStatus('loading');
    if (!navigator.geolocation) {
      toast({
        variant: "destructive",
        title: "Geolocation Error",
        description: "Geolocation is not supported by your browser.",
      });
      setStatus('idle');
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        console.log('SOS Alert Sent!', { latitude, longitude });
        // Here you would send the data to your backend
        setTimeout(() => {
          setStatus('sent');
          toast({
            title: "SOS Alert Sent",
            description: "Help is on the way. A volunteer has been notified.",
          });
        }, 2000); // Simulate network delay
      },
      (error) => {
        console.error('Geolocation Error:', error);
        toast({
          variant: "destructive",
          title: "Could not get location",
          description: "Please enable location services and try again.",
        });
        setStatus('idle');
      }
    );
  };

  if (status === 'sent') {
    return (
        <div className="flex flex-col items-center justify-center p-8 bg-green-100 dark:bg-green-900/20 rounded-full aspect-square w-64 h-64 mx-auto border-4 border-green-500 animate-in fade-in zoom-in-50 duration-500">
            <CheckCircle className="w-24 h-24 text-green-600 dark:text-green-400 mb-4" />
            <p className="text-xl font-bold text-green-800 dark:text-green-200">Alert Sent</p>
            <p className="text-green-700 dark:text-green-300">Help is on the way.</p>
        </div>
    );
  }

  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <Button
          className="relative rounded-full w-64 h-64 shadow-2xl bg-accent hover:bg-accent/90 text-accent-foreground transition-all duration-300 ease-in-out transform hover:scale-105"
          disabled={status === 'loading'}
          aria-label="Send Emergency SOS Alert"
        >
          {status === 'loading' ? (
            <Loader2 className="w-24 h-24 animate-spin" />
          ) : (
            <div className="flex flex-col items-center">
                <Siren className="w-24 h-24" />
                <span className="text-4xl font-bold mt-2 font-headline tracking-wider">SOS</span>
            </div>
          )}
        </Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle className="font-headline">Confirm Emergency Alert</AlertDialogTitle>
          <AlertDialogDescription>
            This will immediately send your location to the nearest volunteer for emergency assistance. Only use this in a genuine emergency.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={handleSendSos} className="bg-destructive hover:bg-destructive/90 text-destructive-foreground">
            Send Alert
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
