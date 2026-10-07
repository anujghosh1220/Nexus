"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useToast } from "@/providers/toast-provider";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Spinner } from "@/components/loading";
import { apiClient } from "@/lib/api";
import type { User } from "@/types/api";

export default function SettingsPage() {
  const queryClient = useQueryClient();
  const { addToast } = useToast();

  const { data: user, isLoading } = useQuery({
    queryKey: ["currentUser"],
    queryFn: async () => {
      const response = await apiClient.get("/auth/me");
      return response.data as User;
    },
  });

  const [firstName, setFirstName] = useState(user?.first_name || "");
  const [lastName, setLastName] = useState(user?.last_name || "");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(false);
  const [showPasswordForm, setShowPasswordForm] = useState(false);

  const updateProfileMutation = useMutation({
    mutationFn: async (data: { first_name: string; last_name: string }) => {
      const response = await apiClient.patch("/auth/me", data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["currentUser"] });
      addToast("Profile updated successfully", "success");
    },
    onError: () => {
      addToast("Failed to update profile", "error");
    },
  });

  const changePasswordMutation = useMutation({
    mutationFn: async (data: { current_password: string; new_password: string }) => {
      const response = await apiClient.post("/auth/change-password", data);
      return response.data;
    },
    onSuccess: () => {
      addToast("Password changed successfully", "success");
      setShowPasswordForm(false);
      setCurrentPassword("");
      setNewPassword("");
    },
    onError: () => {
      addToast("Failed to change password", "error");
    },
  });

  const toggle2FAMutation = useMutation({
    mutationFn: async (enabled: boolean) => {
      if (enabled) {
        await apiClient.post("/2fa/enable");
      } else {
        await apiClient.post("/2fa/disable");
      }
    },
    onSuccess: () => {
      setTwoFactorEnabled(!twoFactorEnabled);
      addToast(twoFactorEnabled ? "2FA disabled" : "2FA enabled", "success");
    },
    onError: () => {
      addToast("Failed to update 2FA settings", "error");
    },
  });

  const handleProfileUpdate = (e: React.FormEvent) => {
    e.preventDefault();
    updateProfileMutation.mutate({ first_name: firstName, last_name: lastName });
  };

  const handlePasswordChange = (e: React.FormEvent) => {
    e.preventDefault();
    changePasswordMutation.mutate({ current_password: currentPassword, new_password: newPassword });
  };

  if (isLoading) {
    return <Spinner size="lg" />;
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold">Settings</h1>
      <p className="mt-1 text-muted-foreground">Manage your account settings</p>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Profile</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleProfileUpdate} className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <label className="text-sm font-medium">First Name</label>
                <Input
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  disabled={updateProfileMutation.isPending}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Last Name</label>
                <Input
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  disabled={updateProfileMutation.isPending}
                />
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Email</label>
              <p className="text-sm text-muted-foreground">{user?.email}</p>
            </div>
            <Button type="submit" disabled={updateProfileMutation.isPending}>
              {updateProfileMutation.isPending ? "Saving..." : "Save Changes"}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Two-Factor Authentication</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">{twoFactorEnabled ? "Enabled" : "Disabled"}</p>
              <p className="text-sm text-muted-foreground">
                {twoFactorEnabled ? "Your account is protected with 2FA" : "Add an extra layer of security"}
              </p>
            </div>
            <Button
              variant={twoFactorEnabled ? "destructive" : "default"}
              onClick={() => toggle2FAMutation.mutate(!twoFactorEnabled)}
              disabled={toggle2FAMutation.isPending}
            >
              {toggle2FAMutation.isPending ? "Updating..." : twoFactorEnabled ? "Disable 2FA" : "Enable 2FA"}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Change Password</CardTitle>
        </CardHeader>
        <CardContent>
          {!showPasswordForm ? (
            <Button variant="outline" onClick={() => setShowPasswordForm(true)}>
              Change Password
            </Button>
          ) : (
            <form onSubmit={handlePasswordChange} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Current Password</label>
                <Input
                  type="password"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  disabled={changePasswordMutation.isPending}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">New Password</label>
                <Input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  disabled={changePasswordMutation.isPending}
                />
              </div>
              <div className="flex gap-3">
                <Button type="submit" disabled={changePasswordMutation.isPending}>
                  {changePasswordMutation.isPending ? "Updating..." : "Change Password"}
                </Button>
                <Button type="button" variant="outline" onClick={() => { setShowPasswordForm(false); setCurrentPassword(""); setNewPassword(""); }}>
                  Cancel
                </Button>
              </div>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
