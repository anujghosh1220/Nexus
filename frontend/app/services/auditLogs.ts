import { apiClient } from "@/lib/api";
import type { AuditLog } from "@/types/api";

export async function getAuditLogs(): Promise<AuditLog[]> {
  const response = await apiClient.get("/audit-logs");
  return response.data;
}
