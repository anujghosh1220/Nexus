"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { useParams } from "next/navigation";
import { useState } from "react";
import { useToast } from "@/providers/toast-provider";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Spinner } from "@/components/loading";
import type { Organization, Membership } from "@/types/api";

export default function OrganizationDetailPage() {
  const params = useParams();
  const orgId = params.id as string;
  const queryClient = useQueryClient();
  const { addToast } = useToast();
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<"ADMIN" | "MANAGER" | "MEMBER" | "VIEWER">("MEMBER");

  const { data: org, isLoading: orgLoading } = useQuery({
    queryKey: ["organization", orgId],
    queryFn: async () => {
      const response = await apiClient.get(`/organizations/${orgId}`);
      return response.data as Organization;
    },
    enabled: !!orgId,
  });

  const { data: members, isLoading: membersLoading } = useQuery({
    queryKey: ["organization", orgId, "members"],
    queryFn: async () => {
      const response = await apiClient.get(`/organizations/${orgId}/members`);
      return response.data as Membership[];
    },
    enabled: !!orgId,
  });

  const inviteMutation = useMutation({
    mutationFn: async (data: { email: string; role: string }) => {
      const response = await apiClient.post(`/organizations/${orgId}/members`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["organization", orgId, "members"] });
      addToast("Member invited successfully", "success");
      setEmail("");
    },
    onError: () => {
      addToast("Failed to invite member", "error");
    },
  });

  const handleInvite = (e: React.FormEvent) => {
    e.preventDefault();
    inviteMutation.mutate({ email, role });
  };

  if (orgLoading || membersLoading) {
    return <Spinner size="lg" />;
  }

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">{org?.name}</h1>
        <p className="mt-1 text-muted-foreground">/{org?.slug}</p>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Invite Member</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleInvite} className="flex gap-4">
            <Input
              placeholder="user@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={inviteMutation.isPending}
            />
            <select
              value={role}
              onChange={(e) => setRole(e.target.value as any)}
              disabled={inviteMutation.isPending}
              className="rounded-md border border-input bg-background px-3 py-2 text-sm"
            >
              <option value="MEMBER">Member</option>
              <option value="ADMIN">Admin</option>
              <option value="MANAGER">Manager</option>
              <option value="VIEWER">Viewer</option>
            </select>
            <Button type="submit" disabled={inviteMutation.isPending}>
              {inviteMutation.isPending ? "Inviting..." : "Invite"}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Members</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {members?.map((member) => (
              <div key={member.id} className="flex items-center justify-between rounded-md border p-3">
                <div>
                  <p className="font-medium">{member.user?.email || member.user_id}</p>
                  <p className="text-sm text-muted-foreground">{member.role}</p>
                </div>
                <span className="rounded-full bg-secondary px-3 py-1 text-xs font-medium">{member.status}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
