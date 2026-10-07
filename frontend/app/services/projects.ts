import { apiClient } from "@/lib/api";
import type { Project } from "@/types/api";

export async function getProjects(): Promise<Project[]> {
  const response = await apiClient.get("/projects");
  return response.data;
}

export async function createProject(data: { name: string; description?: string; status?: string }): Promise<Project> {
  const response = await apiClient.post("/projects", data);
  return response.data;
}

export async function getProject(id: string): Promise<Project> {
  const response = await apiClient.get(`/projects/${id}`);
  return response.data;
}

export async function updateProject(id: string, data: { name?: string; description?: string; status?: string }): Promise<Project> {
  const response = await apiClient.patch(`/projects/${id}`, data);
  return response.data;
}

export async function deleteProject(id: string): Promise<void> {
  await apiClient.delete(`/projects/${id}`);
}
