import Link from 'next/link';

export function Footer() {
  return (
    <footer className="bg-card text-card-foreground border-t mt-auto">
      <div className="container mx-auto py-8 px-4 md:px-6">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-4 md:mb-0">
            <p className="text-lg font-bold font-headline text-primary">Drishti</p>
            <p className="text-sm text-muted-foreground">Improving Safety at Large Public Events</p>
          </div>
          <div className="flex flex-col md:flex-row items-center gap-4 md:gap-8">
            <div className="text-center md:text-left">
              <h3 className="font-semibold mb-2">Contact Us</h3>
              <p className="text-sm text-muted-foreground">contact@drishti.com</p>
              <p className="text-sm text-muted-foreground">+1 (234) 567-890</p>
            </div>
          </div>
        </div>
        <div className="mt-8 pt-4 border-t border-border text-center text-muted-foreground text-sm">
          <p>&copy; {new Date().getFullYear()} Drishti. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}

