"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ArrowRight,
  Building2,
  ClipboardList,
  Code2,
  FolderKanban,
  Shield,
  Users,
  Sparkles,
  Zap,
  ShieldCheck,
  HardDrive,
} from "lucide-react";
import { cn } from "@/lib/utils";

function useInView(options?: IntersectionObserverInit) {
  const ref = useRef<HTMLDivElement>(null);
  const [isInView, setIsInView] = useState(false);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        setIsInView(true);
        observer.unobserve(element);
      }
    }, options);

    observer.observe(element);
    return () => observer.disconnect();
  }, [options]);

  return { ref, isInView };
}

function AnimatedSection({
  children,
  className,
  delay = 0,
}: {
  children: React.ReactNode;
  className?: string;
  delay?: number;
}) {
  const { ref, isInView } = useInView({ threshold: 0.1 });

  return (
    <div
      ref={ref}
      className={cn(
        "transition-all duration-700 ease-out",
        isInView ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8",
        className
      )}
      style={{ transitionDelay: `${delay}ms` }}
    >
      {children}
    </div>
  );
}

export default function Home() {
  const router = useRouter();
  const features = [
    {
      icon: Building2,
      title: "Multi-Tenant Architecture",
      description:
        "Isolated workspaces with secure tenant separation for enterprise-grade multi-organization deployments.",
    },
    {
      icon: Users,
      title: "Teams & Projects",
      description:
        "Organize teams, assign roles, and manage projects with granular permissions and real-time collaboration.",
    },
    {
      icon: ClipboardList,
      title: "Task Management",
      description:
        "Kanban boards, task assignments, due dates, and progress tracking with full audit trail.",
    },
    {
      icon: Code2,
      title: "Developer API",
      description:
        "RESTful API with comprehensive documentation, webhooks, SDKs, and interactive playground.",
    },
    {
      icon: ShieldCheck,
      title: "Audit & Security",
      description:
        "Complete audit logging, role-based access control, and enterprise security compliance.",
    },
    {
      icon: HardDrive,
      title: "File Storage",
      description:
        "Secure file uploads with access controls, versioning, and CDN-backed delivery.",
    },
  ];

  return (
    <main className="nexus-grid-bg min-h-screen relative overflow-hidden">
      <nav className="fixed top-0 left-0 right-0 z-50 glass-panel border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <Link href="/" className="flex items-center gap-2">
              <span className="text-xl font-bold tracking-tight nexus-text-gradient">
                NEXUS
              </span>
            </Link>
            <div className="hidden md:flex items-center gap-8">
              <Link
                href="#features"
                className="text-sm text-slate-400 hover:text-white transition-colors"
              >
                Features
              </Link>
              <Link
                href="/login"
                className="text-sm text-slate-400 hover:text-white transition-colors"
              >
                Sign in
              </Link>
              <Link
                href="/login"
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-primary text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-all hover:shadow-[0_0_20px_rgba(59,130,246,0.3)]"
              >
                Get Started
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <section className="relative pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-8">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-medium">
                <Sparkles className="h-3.5 w-3.5" />
                Production-Grade Platform
              </div>
              <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight">
                <span className="block text-white">NEXUS</span>
                <span className="block mt-2 text-3xl sm:text-4xl lg:text-5xl text-slate-400 font-normal">
                  One workspace. Every operation.
                </span>
              </h1>
              <p className="text-lg text-slate-400 max-w-xl leading-relaxed">
                A unified platform for teams, projects, workflows, and APIs. Built for
                scale, designed for developers, and secured for enterprise.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link
                  href="/login"
                  className="inline-flex items-center justify-center gap-2 px-8 py-3.5 rounded-lg bg-gradient-to-r from-primary to-secondary text-white font-medium hover:shadow-[0_0_30px_rgba(59,130,246,0.3)] transition-all duration-300 animate-glow"
                >
                  Get Started
                  <ArrowRight className="h-4 w-4" />
                </Link>
                <Link
                  href="#features"
                  className="inline-flex items-center justify-center gap-2 px-8 py-3.5 rounded-lg border border-white/10 bg-white/5 text-white font-medium hover:bg-white/10 transition-all duration-300"
                >
                  Explore the platform
                </Link>
              </div>
              <div className="flex items-center gap-6 pt-4">
                <div className="flex items-center gap-2 text-sm text-slate-400">
                  <Zap className="h-4 w-4 text-accent" />
                  Fast API
                </div>
                <div className="flex items-center gap-2 text-sm text-slate-400">
                  <Shield className="h-4 w-4 text-accent" />
                  Enterprise Security
                </div>
                <div className="flex items-center gap-2 text-sm text-slate-400">
                  <Users className="h-4 w-4 text-accent" />
                  Team Collaboration
                </div>
              </div>
            </div>

            <div className="relative flex items-center justify-center">
              <div className="relative w-80 h-80 sm:w-96 sm:h-96">
                <div className="absolute inset-0 rounded-full border border-primary/20 animate-pulse-soft" />
                <div className="absolute inset-4 rounded-full border border-primary/15 animate-pulse-soft" style={{ animationDelay: "0.5s" }} />
                <div className="absolute inset-8 rounded-full border border-primary/10 animate-pulse-soft" style={{ animationDelay: "1s" }} />

                <div className="absolute inset-0 animate-spin" style={{ animationDuration: "20s" }}>
                  <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-primary shadow-[0_0_10px_rgba(59,130,246,0.5)]" />
                </div>
                <div className="absolute inset-0 animate-spin" style={{ animationDuration: "30s", animationDirection: "reverse" }}>
                  <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 w-2.5 h-2.5 rounded-full bg-accent shadow-[0_0_10px_rgba(34,211,238,0.5)]" />
                </div>
                <div className="absolute inset-0 animate-spin" style={{ animationDuration: "25s" }}>
                  <div className="absolute top-1/2 right-0 translate-x-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-secondary shadow-[0_0_10px_rgba(99,102,241,0.5)]" />
                </div>

                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="relative">
                    <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-[0_0_40px_rgba(59,130,246,0.3)] animate-node-float">
                      <span className="text-3xl font-bold text-white tracking-tighter">N</span>
                    </div>
                    <div className="absolute -inset-4 rounded-3xl border border-primary/20 animate-pulse-soft" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="features" className="py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <AnimatedSection className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
              Everything you need
            </h2>
            <p className="text-lg text-slate-400 max-w-2xl mx-auto">
              A complete platform for modern teams to build, manage, and scale their operations.
            </p>
          </AnimatedSection>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <AnimatedSection key={feature.title} delay={index * 100}>
                <div className="group relative h-full p-6 rounded-xl border border-white/10 bg-white/[0.02] hover:bg-white/[0.05] hover:border-primary/30 transition-all duration-300 cursor-default">
                  <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                  <div className="relative">
                    <div className="w-12 h-12 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center mb-4 group-hover:border-primary/40 transition-colors">
                      <feature.icon className="h-6 w-6 text-primary" />
                    </div>
                    <h3 className="text-lg font-semibold text-white mb-2">
                      {feature.title}
                    </h3>
                    <p className="text-sm text-slate-400 leading-relaxed">
                      {feature.description}
                    </p>
                  </div>
                </div>
              </AnimatedSection>
            ))}
          </div>
        </div>
      </section>

      <section className="py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <AnimatedSection>
            <div className="relative rounded-2xl border border-primary/20 bg-gradient-to-br from-primary/5 to-secondary/5 p-12 text-center overflow-hidden">
              <div className="absolute inset-0 nexus-grid-bg opacity-50" />
              <div className="relative">
                <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
                  Ready to get started?
                </h2>
                <p className="text-lg text-slate-400 mb-8 max-w-xl mx-auto">
                  Join teams already using NEXUS to streamline their operations and boost productivity.
                </p>
                <Link
                  href="/login"
                  className="inline-flex items-center gap-2 px-8 py-3.5 rounded-lg bg-gradient-to-r from-primary to-secondary text-white font-medium hover:shadow-[0_0_30px_rgba(59,130,246,0.3)] transition-all duration-300 animate-glow"
                >
                  Get Started
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>
            </div>
          </AnimatedSection>
        </div>
      </section>

      <footer className="border-t border-white/10 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="text-lg font-bold tracking-tight nexus-text-gradient">
              NEXUS
            </span>
          </div>
          <p className="text-sm text-slate-500">
            &copy; {new Date().getFullYear()} NEXUS. All rights reserved.
          </p>
        </div>
      </footer>
    </main>
  );
}
