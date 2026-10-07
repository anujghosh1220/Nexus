export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="text-center">
        <h1 className="text-4xl font-bold tracking-tight text-foreground">NEXUS</h1>
        <p className="mt-2 text-lg text-muted-foreground">One workspace. Every operation.</p>
        <div className="mt-8">
          <a
            href="/login"
            className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-8 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
          >
            Get Started
          </a>
        </div>
      </div>
    </div>
  );
}
