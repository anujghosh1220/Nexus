"use client";

import { type ReactNode } from "react";
import { AuthRedirect } from "@/components/auth-redirect";
import { DashboardSidebar } from "@/components/dashboard-sidebar";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <AuthRedirect>
      <div className="flex h-screen">
        <DashboardSidebar />
        <main className="flex-1 overflow-y-auto bg-background">
          {children}
        </main>
      </div>
    </AuthRedirect>
  );
}
