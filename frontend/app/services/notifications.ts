import { apiClient } from "@/lib/api";
import type { Notification } from "@/types/api";

export async function getNotifications(): Promise<Notification[]> {
  const response = await apiClient.get("/notifications");
  return response.data;
}

export async function markNotificationRead(id: string): Promise<Notification> {
  const response = await apiClient.post(`/notifications/${id}/read`);
  return response.data;
}

export async function markAllNotificationsRead(): Promise<void> {
  await apiClient.post("/notifications/read-all");
}
