import { apiClient } from "@/lib/api";
import type { Task } from "@/types/api";

export async function getTasks(): Promise<Task[]> {
  const response = await apiClient.get("/tasks");
  return response.data;
}

export async function createTask(data: { title: string; description?: string; status?: string; priority?: string; project_id: string; assignee_id?: string }): Promise<Task> {
  const response = await apiClient.post("/tasks", data);
  return response.data;
}

export async function getTask(id: string): Promise<Task> {
  const response = await apiClient.get(`/tasks/${id}`);
  return response.data;
}

export async function updateTask(id: string, data: { title?: string; description?: string; status?: string; priority?: string; assignee_id?: string }): Promise<Task> {
  const response = await apiClient.patch(`/tasks/${id}`, data);
  return response.data;
}

export async function deleteTask(id: string): Promise<void> {
  await apiClient.delete(`/tasks/${id}`);
}
