import { apiClient } from "@/lib/api";
import type { ApiKey } from "@/types/api";

export async function getApiKeys(): Promise<ApiKey[]> {
  const response = await apiClient.get("/api-keys");
  return response.data;
}

export async function createApiKey(data: { name: string }): Promise<ApiKey> {
  const response = await apiClient.post("/api-keys", data);
  return response.data;
}

export async function getApiKey(id: string): Promise<ApiKey> {
  const response = await apiClient.get(`/api-keys/${id}`);
  return response.data;
}

export async function revokeApiKey(id: string): Promise<void> {
  await apiClient.post(`/api-keys/${id}/revoke`);
}
