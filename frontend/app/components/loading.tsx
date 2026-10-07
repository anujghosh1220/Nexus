import React from "react";

interface SpinnerProps {
  size?: "sm" | "md" | "lg";
  variant?: "default" | "nexus";
}

export function Spinner({ size = "md", variant = "default" }: SpinnerProps) {
  const sizeClasses = {
    sm: "h-4 w-4",
    md: "h-8 w-8",
    lg: "h-12 w-12",
  };

  if (variant === "nexus") {
    return (
      <div className="relative">
        <div className="absolute inset-0 rounded-full border border-primary/20 animate-ping" />
        <div className={`${sizeClasses[size]} relative rounded-full border-2 border-primary/30 border-t-primary animate-spin`} />
      </div>
    );
  }

  return (
    <div className={`${sizeClasses[size]} animate-spin rounded-full border-2 border-muted border-t-primary`} />
  );
}

export function LoadingScreen({ message = "Loading..." }: { message?: string }) {
  return (
    <div className="flex min-h-screen items-center justify-center nexus-grid-bg">
      <div className="flex flex-col items-center gap-3">
        <Spinner size="lg" variant="nexus" />
        <p className="text-sm text-slate-400 animate-pulse-soft">{message}</p>
      </div>
    </div>
  );
}

export function LoadingOverlay({ message = "Loading..." }: { message?: string }) {
  return (
    <div className="absolute inset-0 flex items-center justify-center bg-nexus-background/80 backdrop-blur-sm">
      <div className="flex flex-col items-center gap-3">
        <Spinner size="md" variant="nexus" />
        <p className="text-sm text-slate-400 animate-pulse-soft">{message}</p>
      </div>
    </div>
  );
}

export function NexusCoreLoader({ message = "Initializing NEXUS CORE..." }: { message?: string }) {
  return (
    <div className="flex min-h-screen items-center justify-center nexus-grid-bg">
      <div className="flex flex-col items-center gap-6">
        <div className="relative w-24 h-24">
          <div className="absolute inset-0 rounded-full border border-primary/30 animate-ping" style={{ animationDuration: "2s" }} />
          <div className="absolute inset-2 rounded-full border border-primary/20 animate-ping" style={{ animationDuration: "2s", animationDelay: "0.3s" }} />
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-[0_0_30px_rgba(59,130,246,0.3)] animate-pulse-soft">
              <span className="text-lg font-bold text-white">N</span>
            </div>
          </div>
        </div>
        <div className="text-center">
          <p className="text-sm font-medium text-white mb-1">NEXUS CORE</p>
          <p className="text-xs text-slate-400 animate-pulse-soft">{message}</p>
        </div>
      </div>
    </div>
  );
}
