"use client";

import { QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "./auth-provider";
import { queryClient } from "@/lib/query-client";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>{children}</AuthProvider>
    </QueryClientProvider>
  );
}
