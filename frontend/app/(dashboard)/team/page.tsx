"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useToast } from "@/providers/toast-provider";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Spinner } from "@/components/loading";
import { getTeams, createTeam, deleteTeam } from "@/services/teams";
import type { Team } from "@/types/api";

export default function TeamPage() {
  const queryClient = useQueryClient();
  const { addToast } = useToast();
  const [showCreate, setShowCreate] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [orgId, setOrgId] = useState("");
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);

  const { data: teams, isLoading } = useQuery({
    queryKey: ["teams"],
    queryFn: getTeams,
  });

  const createMutation = useMutation({
    mutationFn: async (data: { name: string; description?: string; organization_id: string }) => {
      const response = await createTeam(data);
      return response;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["teams"] });
      addToast("Team created successfully", "success");
      setShowCreate(false);
      setName("");
      setDescription("");
      setOrgId("");
    },
    onError: () => {
      addToast("Failed to create team", "error");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      await deleteTeam(id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["teams"] });
      addToast("Team deleted", "success");
      setConfirmDeleteId(null);
    },
    onError: () => {
      addToast("Failed to delete team", "error");
    },
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate({ name, description: description || undefined, organization_id: orgId });
  };

  if (isLoading) {
    return <Spinner size="lg" />;
  }

  return (
    <div className="p-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Teams</h1>
          <p className="mt-1 text-muted-foreground">Manage your teams</p>
        </div>
        <Button onClick={() => setShowCreate(!showCreate)}>
          {showCreate ? "Cancel" : "Create Team"}
        </Button>
      </div>

      {showCreate && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Create Team</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Name</label>
                <Input
                  placeholder="Engineering Team"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  disabled={createMutation.isPending}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Description</label>
                <Input
                  placeholder="Optional description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  disabled={createMutation.isPending}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Organization ID</label>
                <Input
                  placeholder="Organization ID"
                  value={orgId}
                  onChange={(e) => setOrgId(e.target.value)}
                  disabled={createMutation.isPending}
                />
              </div>
              <Button type="submit" disabled={createMutation.isPending}>
                {createMutation.isPending ? "Creating..." : "Create"}
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {teams?.map((team: Team) => (
          <Card key={team.id}>
            <CardHeader>
              <CardTitle>{team.name}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">{team.description || "No description"}</p>
              <p className="text-xs text-muted-foreground mt-2">Org: {team.organization_id}</p>
              <div className="mt-3">
                <Button
                  variant="destructive"
                  size="sm"
                  disabled={deleteMutation.isPending && confirmDeleteId === team.id}
                  onClick={() => setConfirmDeleteId(team.id)}
                >
                  Delete
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
        {teams?.length === 0 && (
          <Card>
            <CardContent className="pt-6">
              <p className="text-center text-muted-foreground">No teams yet. Create one to get started.</p>
            </CardContent>
          </Card>
        )}
      </div>

      {confirmDeleteId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Confirm Delete</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                Are you sure you want to delete this team? This action cannot be undone.
              </p>
              <div className="flex gap-3">
                <Button
                  variant="destructive"
                  onClick={() => deleteMutation.mutate(confirmDeleteId)}
                  disabled={deleteMutation.isPending}
                >
                  {deleteMutation.isPending ? "Deleting..." : "Delete"}
                </Button>
                <Button variant="outline" onClick={() => setConfirmDeleteId(null)}>
                  Cancel
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
