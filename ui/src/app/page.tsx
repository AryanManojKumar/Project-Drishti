
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Zap, ShieldCheck, Eye, Users, Gauge, Siren, User, LifeBuoy } from 'lucide-react';
import { Footer } from '@/components/footer';
import { Header } from '@/components/header';
import Image from 'next/image';

export default function HomePage() {
  return (
    <div className="flex flex-col min-h-screen bg-background text-foreground">
      <Header />
      <main className="flex-grow">
        {/* Hero Section */}
        <section className="relative text-center py-24 md:py-32 lg:py-40 overflow-hidden">
           <div
            className="absolute inset-0 bg-cover bg-center z-[-1] opacity-20"
            style={{backgroundImage: "url('https://placehold.co/1920x1080.png')", backgroundBlendMode: 'overlay'}}
            data-ai-hint="crowd event"
          ></div>
          <div className="container relative mx-auto px-4 animate-in fade-in slide-in-from-bottom-8 duration-1000">
            <h1 className="font-headline text-4xl md:text-6xl font-bold text-primary">Drishti Guard</h1>
            <p className="mt-4 text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto">
              Revolutionizing public safety with an AI-powered co-pilot for event security, connecting attendees, volunteers, and command in real-time.
            </p>
            <div className="mt-8 flex justify-center gap-4">
              <Link href="/login" passHref>
                <Button size="lg" className="bg-primary text-primary-foreground hover:bg-primary/90">
                  Access Your Role
                </Button>
              </Link>
              <Link href="#features" passHref>
                <Button size="lg" variant="outline">
                  Learn More
                </Button>
              </Link>
            </div>
          </div>
        </section>

        {/* Role Cards Section */}
        <section id="roles" className="py-20 bg-secondary">
          <div className="container mx-auto px-4 animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-200">
            <div className="text-center mb-16">
              <h2 className="font-headline text-3xl md:text-4xl font-bold">Choose Your Role</h2>
              <p className="mt-2 text-muted-foreground max-w-2xl mx-auto">
                Select your role to access the tools and information you need to stay safe and effective.
              </p>
            </div>
            <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
              <Card className="text-center bg-card hover:bg-card/90 transition-all duration-300 transform hover:-translate-y-2">
                <CardHeader>
                   <div className="mx-auto bg-primary/10 p-4 rounded-full mb-4 w-fit">
                    <User className="w-12 h-12 text-primary" />
                  </div>
                  <CardTitle className="font-headline text-2xl">Are you an Attendee?</CardTitle>
                  <CardDescription>
                    Your safety is our priority. Access the emergency SOS feature to instantly alert our team if you need help.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Link href="/login" passHref>
                    <Button>Attendee Login</Button>
                  </Link>
                </CardContent>
              </Card>
              <Card className="text-center bg-card hover:bg-card/90 transition-all duration-300 transform hover:-translate-y-2">
                <CardHeader>
                   <div className="mx-auto bg-primary/10 p-4 rounded-full mb-4 w-fit">
                    <ShieldCheck className="w-12 h-12 text-primary" />
                  </div>
                  <CardTitle className="font-headline text-2xl">Are you a Volunteer?</CardTitle>
                  <CardDescription>
                    Join the live feed to receive dispatches, anomaly alerts, and crowd insights to keep the event safe.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Link href="/login" passHref>
                    <Button>Volunteer Login</Button>
                  </Link>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="py-20 md:py-28 bg-background">
          <div className="container mx-auto px-4 max-w-7xl animate-in fade-in slide-in-from-bottom-16 duration-1000 delay-400">
            <div className="text-center mb-16">
              <h2 className="font-headline text-3xl md:text-4xl font-bold">A New Paradigm in Event Safety</h2>
              <p className="mt-2 text-muted-foreground max-w-2xl mx-auto">
                Drishti leverages cutting-edge multimodal AI to provide unparalleled situational awareness and proactive threat mitigation.
              </p>
            </div>

            {/* Feature 1: Multimodal Anomaly Detection */}
            <div className="grid md:grid-cols-2 gap-12 items-center mb-24">
              <div className="relative aspect-video rounded-lg shadow-2xl overflow-hidden group">
                <Image
                  src="/anomalies.png"
                  alt="Anomaly detection visualization"
                  width={600}
                  height={400}
                  className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-500"
                  data-ai-hint="security camera feed"
                />
                 <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent"></div>
                 <div className="absolute bottom-4 left-4 text-white">
                    <h4 className="font-bold text-lg">Live Threat Identification</h4>
                    <p className="text-sm">Fusing video feeds with attendee alerts.</p>
                 </div>
              </div>
              <div>
                <div className="flex items-center gap-3">
                    <div className="p-3 bg-primary/10 rounded-full">
                        <Eye className="w-6 h-6 text-primary" />
                    </div>
                    <h3 className="font-headline text-2xl md:text-3xl font-bold">Multimodal Anomaly Detection</h3>
                </div>
                <p className="mt-4 text-muted-foreground">
                  Our system continuously scans live video feeds and ingests attendee SOS alerts to detect anomalies. It identifies visual signatures of smoke, fire, or panicked crowd surges and pinpoints user-activated distress signals. The AI agent then triggers immediate, high-priority dispatch alerts to the nearest volunteers for rapid, targeted response.
                </p>
                <div className="mt-6 grid grid-cols-2 gap-4 text-sm">
                    <div className="flex items-center gap-2 p-3 bg-secondary rounded-lg">
                        <Siren className="w-5 h-5 text-primary" />
                        <span>Attendee SOS Integration</span>
                    </div>
                    <div className="flex items-center gap-2 p-3 bg-secondary rounded-lg">
                        <Zap className="w-5 h-5 text-primary" />
                        <span>Video Anomaly Detection</span>
                    </div>
                     <div className="flex items-center gap-2 p-3 bg-secondary rounded-lg">
                        <ShieldCheck className="w-5 h-5 text-primary" />
                        <span>Proximity-Based Dispatch</span>
                    </div>
                     <div className="flex items-center gap-2 p-3 bg-secondary rounded-lg">
                        <Users className="w-5 h-5 text-primary" />
                        <span>Real-time Volunteer Alerts</span>
                    </div>
                </div>
              </div>
            </div>

            {/* Feature 2: Predictive Crowd Analytics */}
            <div className="grid md:grid-cols-2 gap-12 items-center">
               <div className="order-2 md:order-1">
                <div className="flex items-center gap-3">
                    <div className="p-3 bg-primary/10 rounded-full">
                        <Gauge className="w-6 h-6 text-primary" />
                    </div>
                    <h3 className="font-headline text-2xl md:text-3xl font-bold">Predictive Crowd & Safety Insights</h3>
                </div>
                <p className="mt-4 text-muted-foreground">
                  By ingesting real-time video, Drishti analyzes crowd density, velocity, and flow to predict potential bottlenecks 15-20 minutes in advance. These AI-powered CNS (Crowd Navigation System) alerts are sent to all volunteers, enabling proactive crowd management. Volunteers also update their status by acknowledging dispatches with their location, constantly feeding the AI new data for smarter assignments.
                </p>
                <div className="mt-6 grid grid-cols-2 gap-4 text-sm">
                    <div className="flex items-center gap-2 p-3 bg-secondary rounded-lg">
                        <LifeBuoy className="w-5 h-5 text-primary"/>
                        <span>Bottleneck Prediction</span>
                    </div>
                    <div className="flex items-center gap-2 p-3 bg-secondary rounded-lg">
                        <Users className="w-5 h-5 text-primary"/>
                        <span>Density & Flow Analysis</span>
                    </div>
                     <div className="flex items-center gap-2 p-3 bg-secondary rounded-lg">
                        <Siren className="w-5 h-5 text-primary"/>
                        <span>Proactive CNS Alerts</span>
                    </div>
                     <div className="flex items-center gap-2 p-3 bg-secondary rounded-lg">
                        <User className="w-5 h-5 text-primary"/>
                        <span>Location-Aware Volunteers</span>
                    </div>
                </div>
              </div>

               <div className="relative aspect-video rounded-lg shadow-2xl overflow-hidden order-1 md:order-2 group">
                 <Image
                  src="/crowd.png"
                  alt="Crowd analytics dashboard"
                  width={600}
                  height={400}
                  className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-500"
                  data-ai-hint="crowd analytics dashboard"
                />
                 <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent"></div>
                 <div className="absolute bottom-4 left-4 text-white">
                    <h4 className="font-bold text-lg">Venue Insights</h4>
                    <p className="text-sm">Predicting congestion and flow.</p>
                 </div>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="bg-secondary py-20">
            <div className="container mx-auto px-4 text-center animate-in fade-in duration-1000 delay-500">
                 <h2 className="font-headline text-3xl font-bold">Ready to Secure Your Event?</h2>
                 <p className="mt-2 text-muted-foreground max-w-xl mx-auto">
                    Log in to the command center to access live feeds, alerts, and predictive insights.
                 </p>
                 <div className="mt-6">
                    <Link href="/login" passHref>
                        <Button size="lg">Command Center Login</Button>
                    </Link>
                 </div>
            </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
