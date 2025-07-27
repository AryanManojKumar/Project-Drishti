
'use client';

import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { MapPin, Clock } from "lucide-react";
import { cn } from '@/lib/utils';
import { useMemo } from "react";

export interface AlertProps {
  type: 'Dispatch' | 'Anomaly' | 'SOS' | 'CNS';
  title: string;
  time: string;
  description: string;
  location: string;
  showAcknowledge?: boolean;
  onAcknowledge?: () => void;
  isAcknowledged?: boolean;
}

export function AlertCard({ type, title, time, description, location, showAcknowledge, onAcknowledge, isAcknowledged }: AlertProps) {
    const { borderClass, badgeClass, badgeTextClass } = useMemo(() => {
        switch (type) {
            case 'Dispatch':
                return { borderClass: 'border-primary', badgeClass: 'bg-primary text-primary-foreground hover:bg-primary/90', badgeTextClass: 'text-primary-foreground' };
            case 'Anomaly':
                return { borderClass: 'border-yellow-400', badgeClass: 'bg-yellow-400 hover:bg-yellow-400/90', badgeTextClass: 'text-black' };
            case 'SOS':
                return { borderClass: 'border-accent', badgeClass: 'bg-accent text-accent-foreground hover:bg-accent/90', badgeTextClass: 'text-accent-foreground' };
            case 'CNS':
            default:
                return { borderClass: 'border-sky-400', badgeClass: 'bg-sky-500 hover:bg-sky-500/90', badgeTextClass: 'text-white' };
        }
    }, [type]);

  return (
    <Card className={cn("flex flex-col h-full shadow-md hover:shadow-lg transition-shadow duration-300 border-l-4 bg-secondary text-secondary-foreground", borderClass)}>
      <CardHeader>
        <div className="flex justify-between items-start gap-4">
          <h3 className="font-headline text-xl font-semibold text-foreground">{title}</h3>
          <Badge className={cn(badgeClass, badgeTextClass)}>{type}</Badge>
        </div>
        <div className="flex items-center text-xs text-muted-foreground pt-1">
          <Clock className="w-3 h-3 mr-1.5" />
          <span>{time}</span>
        </div>
      </CardHeader>
      <CardContent className="flex-grow space-y-4">
        <p className="text-sm text-muted-foreground">{description}</p>
        <div className="flex items-center text-sm">
          <MapPin className="w-4 h-4 mr-2 text-primary" />
          <span className="text-foreground">{location}</span>
        </div>
      </CardContent>
      {showAcknowledge && (
        <CardFooter>
          <Button 
            className={cn("w-full", isAcknowledged ? "bg-green-600 hover:bg-green-700" : "bg-primary hover:bg-primary/90", "text-white")}
            onClick={onAcknowledge}
            disabled={isAcknowledged}
          >
            {isAcknowledged ? 'Acknowledged' : 'Acknowledge'}
          </Button>
        </CardFooter>
      )}
    </Card>
  );
}
