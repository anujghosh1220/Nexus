import { apiClient } from "@/lib/api";
import type { File } from "@/types/api";

export async function getFiles(): Promise<File[]> {
  const response = await apiClient.get("/files");
  return response.data;
}

export async function uploadFile(file: globalThis.File): Promise<File> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await apiClient.post("/files/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

export async function downloadFile(id: string): Promise<Blob> {
  const response = await apiClient.get(`/files/${id}/download`, {
    responseType: "blob",
  });
  return response.data;
}

export async function deleteFile(id: string): Promise<void> {
  await apiClient.delete(`/files/${id}`);
}
