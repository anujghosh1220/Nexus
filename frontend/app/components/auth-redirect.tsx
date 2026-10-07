"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";
import { LoadingScreen } from "@/components/loading";

const publicPaths = ["/login", "/register", "/forgot-password", "/reset-password"];

export function AuthRedirect({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (isLoading) return;

    const isPublic = publicPaths.some((path) => pathname === path || pathname.startsWith(path));

    if (!isAuthenticated && !isPublic) {
      router.replace("/login");
    } else if (isAuthenticated && isPublic) {
      router.replace("/dashboard");
    }
  }, [isAuthenticated, isLoading, pathname, router]);

  if (isLoading) {
    return <LoadingScreen message="Loading..." />;
  }

  return <>{children}</>;
}
