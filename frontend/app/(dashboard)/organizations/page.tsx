"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { useState } from "react";
import { useToast } from "@/providers/toast-provider";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Spinner, LoadingOverlay } from "@/components/loading";
import type { Organization } from "@/types/api";

export default function OrganizationsPage() {
  const queryClient = useQueryClient();
  const { addToast } = useToast();
  const [showCreate, setShowCreate] = useState(false);
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");

  const { data: orgs, isLoading } = useQuery({
    queryKey: ["organizations"],
    queryFn: async () => {
      const response = await apiClient.get("/organizations");
      return response.data as Organization[];
    },
  });

  const createMutation = useMutation({
    mutationFn: async (data: { name: string; slug: string }) => {
      const response = await apiClient.post("/organizations", data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["organizations"] });
      addToast("Organization created successfully", "success");
      setShowCreate(false);
      setName("");
      setSlug("");
    },
    onError: () => {
      addToast("Failed to create organization", "error");
    },
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate({ name, slug });
  };

  if (isLoading) {
    return <Spinner size="lg" />;
  }

  return (
    <div className="p-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Organizations</h1>
          <p className="mt-1 text-muted-foreground">Manage your workspaces</p>
        </div>
        <Button onClick={() => setShowCreate(!showCreate)}>
          {showCreate ? "Cancel" : "Create Organization"}
        </Button>
      </div>

      {showCreate && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Create Organization</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Name</label>
                  <Input
                    placeholder="Acme Inc."
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    disabled={createMutation.isPending}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Slug</label>
                  <Input
                    placeholder="acme-inc"
                    value={slug}
                    onChange={(e) => setSlug(e.target.value)}
                    disabled={createMutation.isPending}
                  />
                </div>
              </div>
              <Button type="submit" disabled={createMutation.isPending}>
                {createMutation.isPending ? "Creating..." : "Create"}
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {orgs?.map((org) => (
          <Card key={org.id}>
            <CardHeader>
              <CardTitle>{org.name}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">/{org.slug}</p>
            </CardContent>
          </Card>
        ))}
        {orgs?.length === 0 && (
          <Card>
            <CardContent className="pt-6">
              <p className="text-center text-muted-foreground">No organizations yet. Create one to get started.</p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
