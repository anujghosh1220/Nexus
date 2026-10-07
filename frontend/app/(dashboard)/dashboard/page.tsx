"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useToast } from "@/providers/toast-provider";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Spinner } from "@/components/loading";
import { apiClient } from "@/lib/api";
import { getProjects } from "@/services/projects";
import { getTasks } from "@/services/tasks";
import { getNotifications } from "@/services/notifications";
import type { Organization, User } from "@/types/api";

export default function DashboardPage() {
  const queryClient = useQueryClient();
  const { addToast } = useToast();
  const [showCreateOrg, setShowCreateOrg] = useState(false);
  const [orgName, setOrgName] = useState("");
  const [orgSlug, setOrgSlug] = useState("");

  const { data: orgs, isLoading: orgsLoading } = useQuery({
    queryKey: ["organizations"],
    queryFn: async () => {
      const response = await apiClient.get("/organizations");
      return response.data as Organization[];
    },
  });

  const { data: projects } = useQuery({
    queryKey: ["projects"],
    queryFn: getProjects,
  });

  const { data: tasks } = useQuery({
    queryKey: ["tasks"],
    queryFn: getTasks,
  });

  const { data: notifications } = useQuery({
    queryKey: ["notifications"],
    queryFn: getNotifications,
  });

  const { data: user } = useQuery({
    queryKey: ["currentUser"],
    queryFn: async () => {
      const response = await apiClient.get("/auth/me");
      return response.data as User;
    },
  });

  const createOrgMutation = useMutation({
    mutationFn: async (data: { name: string; slug: string }) => {
      const response = await apiClient.post("/organizations", data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["organizations"] });
      addToast("Organization created successfully", "success");
      setShowCreateOrg(false);
      setOrgName("");
      setOrgSlug("");
    },
    onError: () => {
      addToast("Failed to create organization", "error");
    },
  });

  const handleCreateOrg = (e: React.FormEvent) => {
    e.preventDefault();
    createOrgMutation.mutate({ name: orgName, slug: orgSlug });
  };

  const unreadNotifications = notifications?.filter((n) => !n.is_read).length || 0;

  if (orgsLoading) {
    return <Spinner size="lg" variant="nexus" />;
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Dashboard</h1>
        <p className="mt-1 text-slate-400">Welcome back, {user?.first_name}!</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card variant="nexus" className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent" />
          <CardHeader>
            <CardTitle>Organizations</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold text-white">{orgs?.length || 0}</p>
            <p className="text-sm text-slate-400">Active workspaces</p>
          </CardContent>
        </Card>

        <Card variant="nexus" className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-secondary/5 to-transparent" />
          <CardHeader>
            <CardTitle>Projects</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold text-white">{projects?.length || 0}</p>
            <p className="text-sm text-slate-400">Total projects</p>
          </CardContent>
        </Card>

        <Card variant="nexus" className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-accent/5 to-transparent" />
          <CardHeader>
            <CardTitle>Tasks</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold text-white">{tasks?.length || 0}</p>
            <p className="text-sm text-slate-400">Total tasks</p>
          </CardContent>
        </Card>

        <Card variant="nexus" className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent" />
          <CardHeader>
            <CardTitle>Notifications</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold text-white">{unreadNotifications}</p>
            <p className="text-sm text-slate-400">Unread notifications</p>
          </CardContent>
        </Card>
      </div>

      <Card variant="nexus" className="mt-8">
        <CardHeader>
          <CardTitle>Your Organizations</CardTitle>
        </CardHeader>
        <CardContent>
          {showCreateOrg && (
            <form onSubmit={handleCreateOrg} className="mb-6 space-y-4 rounded-lg border border-white/10 bg-white/[0.02] p-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-300">Name</label>
                  <Input
                    placeholder="Acme Inc."
                    value={orgName}
                    onChange={(e) => setOrgName(e.target.value)}
                    disabled={createOrgMutation.isPending}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-300">Slug</label>
                  <Input
                    placeholder="acme-inc"
                    value={orgSlug}
                    onChange={(e) => setOrgSlug(e.target.value)}
                    disabled={createOrgMutation.isPending}
                  />
                </div>
              </div>
              <div className="flex gap-3">
                <Button type="submit" disabled={createOrgMutation.isPending} variant="nexus">
                  {createOrgMutation.isPending ? "Creating..." : "Create"}
                </Button>
                <Button type="button" variant="outline" onClick={() => setShowCreateOrg(false)}>
                  Cancel
                </Button>
              </div>
            </form>
          )}

          {orgs?.length === 0 ? (
            <div className="text-center">
              <p className="text-slate-400 mb-4">No organizations yet. Create one to get started.</p>
              {!showCreateOrg && (
                <Button onClick={() => setShowCreateOrg(true)} variant="nexus">
                  Create Organization
                </Button>
              )}
            </div>
          ) : (
            <>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {orgs?.map((org) => (
                  <Card key={org.id} variant="nexus">
                    <CardHeader>
                      <CardTitle>{org.name}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-slate-400">/{org.slug}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
              {!showCreateOrg && (
                <div className="mt-4">
                  <Button variant="outline" onClick={() => setShowCreateOrg(true)}>
                    Create Organization
                  </Button>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
