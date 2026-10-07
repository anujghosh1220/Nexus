import { apiClient } from "@/lib/api";
import type { Team } from "@/types/api";

export async function getTeams(): Promise<Team[]> {
  const response = await apiClient.get("/teams");
  return response.data;
}

export async function createTeam(data: { name: string; description?: string; organization_id: string }): Promise<Team> {
  const response = await apiClient.post("/teams", data);
  return response.data;
}

export async function getTeam(id: string): Promise<Team> {
  const response = await apiClient.get(`/teams/${id}`);
  return response.data;
}

export async function updateTeam(id: string, data: { name?: string; description?: string }): Promise<Team> {
  const response = await apiClient.patch(`/teams/${id}`, data);
  return response.data;
}

export async function deleteTeam(id: string): Promise<void> {
  await apiClient.delete(`/teams/${id}`);
}
