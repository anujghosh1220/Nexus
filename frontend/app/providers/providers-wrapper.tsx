"use client";

import { type ReactNode } from "react";
import { Providers } from "@/providers/providers";
import { ToastProvider } from "@/providers/toast-provider";

export function ProvidersWithToast({ children }: { children: ReactNode }) {
  return (
    <Providers>
      <ToastProvider>{children}</ToastProvider>
    </Providers>
  );
}
