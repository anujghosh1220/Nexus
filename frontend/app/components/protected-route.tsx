"use client";

import { LoadingScreen } from "@/components/loading";
import { useRouter } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  if (isLoading) {
    return <LoadingScreen message="Loading..." />;
  }

  if (!isAuthenticated) {
    return null;
  }

  return <>{children}</>;
}
