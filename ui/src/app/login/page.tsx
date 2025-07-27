
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Header } from '@/components/header';
import { Footer } from '@/components/footer';
import { useToast } from '@/hooks/use-toast';
import { DUMMY_ATTENDEE, DUMMY_VOLUNTEERS } from '@/lib/users';
import Link from 'next/link';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const router = useRouter();
  const { toast } = useToast();
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  const handleLogin = async () => {
    if (!isClient) return;

    if (email === DUMMY_ATTENDEE.email && password === DUMMY_ATTENDEE.password) {
      localStorage.setItem('user', JSON.stringify({ name: DUMMY_ATTENDEE.name, role: 'attendee' }));
      router.push('/attendee');
      return;
    }

    const volunteer = DUMMY_VOLUNTEERS.find(v => v.email === email && v.password === password);
    if (volunteer) {
        localStorage.setItem('user', JSON.stringify({ name: volunteer.name, role: 'volunteer' }));
        // Don't request location here. It will be requested on the volunteer page when needed.
        router.push('/volunteer');
        return;
    }

    toast({
      variant: 'destructive',
      title: 'Invalid Credentials',
      description: 'Please check your email and password and try again.',
    });
  };

  return (
    <div className="flex flex-col min-h-screen bg-background">
      <Header />
      <main className="flex-grow flex items-center justify-center p-4 md:py-24 bg-gray-100 text-gray-800">
        <Card className="w-full max-w-sm">
          <CardHeader>
            <CardTitle className="text-2xl">Login</CardTitle>
            <CardDescription>
              Enter your email below to login to your account.
            </CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4">
            <div className="grid gap-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="m@example.com"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </CardContent>
          <CardFooter className="flex flex-col">
            <Button className="w-full" onClick={handleLogin} disabled={!isClient}>Login</Button>
            <div className="mt-4 text-center text-sm">
              Don&apos;t have an account?{' '}
              <Link href="/signup" className="underline">
                Sign up
              </Link>
            </div>
          </CardFooter>
        </Card>
      </main>
      <Footer />
    </div>
  );
}
