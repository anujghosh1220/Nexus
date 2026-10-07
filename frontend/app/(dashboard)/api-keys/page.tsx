"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useToast } from "@/providers/toast-provider";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Spinner, LoadingOverlay } from "@/components/loading";
import { getApiKeys, createApiKey, revokeApiKey } from "@/services/apiKeys";
import type { ApiKey } from "@/types/api";

export default function ApiKeysPage() {
  const queryClient = useQueryClient();
  const { addToast } = useToast();
  const [showCreate, setShowCreate] = useState(false);
  const [name, setName] = useState("");
  const [secretKey, setSecretKey] = useState<string | null>(null);
  const [confirmRevokeId, setConfirmRevokeId] = useState<string | null>(null);

  const { data: keys, isLoading } = useQuery({
    queryKey: ["api-keys"],
    queryFn: getApiKeys,
  });

  const createMutation = useMutation({
    mutationFn: createApiKey,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["api-keys"] });
      addToast("API key created", "success");
      setShowCreate(false);
      setName("");
      setSecretKey(data.key || null);
    },
    onError: () => {
      addToast("Failed to create API key", "error");
    },
  });

  const revokeMutation = useMutation({
    mutationFn: async (id: string) => {
      await revokeApiKey(id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["api-keys"] });
      addToast("API key revoked", "success");
      setConfirmRevokeId(null);
    },
    onError: () => {
      addToast("Failed to revoke API key", "error");
    },
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate({ name });
  };

  const activeKeys = keys?.filter((k: ApiKey) => !k.revoked_at) || [];
  const revokedKeys = keys?.filter((k: ApiKey) => k.revoked_at) || [];

  return (
    <div className="p-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">API Keys</h1>
          <p className="mt-1 text-muted-foreground">Manage your API keys</p>
        </div>
        <Button onClick={() => { setShowCreate(!showCreate); setSecretKey(null); }}>
          {showCreate ? "Cancel" : "Create API Key"}
        </Button>
      </div>

      {secretKey && (
        <Card className="mb-6 border-yellow-500">
          <CardHeader>
            <CardTitle className="text-yellow-600">Save Your Secret Key</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-2">
              Copy this key now. You will not be able to see it again.
            </p>
            <code className="block rounded-md bg-muted p-3 text-sm break-all">{secretKey}</code>
          </CardContent>
        </Card>
      )}

      {showCreate && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Create API Key</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Key Name</label>
                <Input
                  placeholder="Production API Key"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
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

      {isLoading && <Spinner size="lg" />}

      {!isLoading && (
        <>
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Active Keys ({activeKeys.length})</CardTitle>
            </CardHeader>
            <CardContent>
              {activeKeys.length === 0 ? (
                <p className="text-center text-muted-foreground">No active API keys.</p>
              ) : (
                <div className="space-y-3">
                  {activeKeys.map((key) => (
                    <div key={key.id} className="flex items-center justify-between rounded-md border p-3">
                      <div>
                        <p className="font-medium">{key.name}</p>
                        <p className="text-sm text-muted-foreground">Prefix: {key.key_prefix}</p>
                        <p className="text-xs text-muted-foreground">Created: {new Date(key.created_at).toLocaleDateString()}</p>
                      </div>
                      <Button
                        variant="destructive"
                        size="sm"
                        disabled={revokeMutation.isPending && confirmRevokeId === key.id}
                        onClick={() => setConfirmRevokeId(key.id)}
                      >
                        Revoke
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Revoked Keys ({revokedKeys.length})</CardTitle>
            </CardHeader>
            <CardContent>
              {revokedKeys.length === 0 ? (
                <p className="text-center text-muted-foreground">No revoked keys.</p>
              ) : (
                <div className="space-y-3">
                  {revokedKeys.map((key) => (
                    <div key={key.id} className="flex items-center justify-between rounded-md border p-3 opacity-60">
                      <div>
                        <p className="font-medium">{key.name}</p>
                        <p className="text-sm text-muted-foreground">Prefix: {key.key_prefix}</p>
                        <p className="text-xs text-muted-foreground">Revoked: {new Date(key.revoked_at!).toLocaleDateString()}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}

      {confirmRevokeId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Confirm Revoke</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                This action cannot be undone. Are you sure you want to revoke this API key?
              </p>
              <div className="flex gap-3">
                <Button
                  variant="destructive"
                  onClick={() => revokeMutation.mutate(confirmRevokeId)}
                  disabled={revokeMutation.isPending}
                >
                  {revokeMutation.isPending ? "Revoking..." : "Revoke"}
                </Button>
                <Button variant="outline" onClick={() => setConfirmRevokeId(null)}>
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
