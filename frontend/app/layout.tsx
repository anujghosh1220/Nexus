import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ProvidersWithToast } from "@/providers/providers-wrapper";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });

export const metadata: Metadata = {
  title: "NEXUS - One workspace. Every operation.",
  description: "Production-grade workspace platform for teams, projects, workflows, and APIs.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className={inter.variable}>
        <ProvidersWithToast>{children}</ProvidersWithToast>
      </body>
    </html>
  );
}
