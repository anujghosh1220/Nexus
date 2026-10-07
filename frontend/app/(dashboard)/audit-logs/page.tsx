"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { getAuditLogs } from "@/services/auditLogs";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Spinner } from "@/components/loading";
import { Input } from "@/components/ui/input";
import type { AuditLog } from "@/types/api";

export default function AuditLogsPage() {
  const [resourceFilter, setResourceFilter] = useState("");
  const [actionFilter, setActionFilter] = useState("");

  const { data: logs, isLoading } = useQuery({
    queryKey: ["audit-logs"],
    queryFn: getAuditLogs,
  });

  const filteredLogs = logs?.filter((log: AuditLog) => {
    const matchResource = !resourceFilter || log.resource_type.toLowerCase().includes(resourceFilter.toLowerCase());
    const matchAction = !actionFilter || log.action.toLowerCase().includes(actionFilter.toLowerCase());
    return matchResource && matchAction;
  }) || [];

  if (isLoading) {
    return <Spinner size="lg" />;
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold">Audit Logs</h1>
      <p className="mt-1 text-muted-foreground">View activity history</p>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm font-medium">Resource Type</label>
              <Input
                placeholder="e.g. project, task"
                value={resourceFilter}
                onChange={(e) => setResourceFilter(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Action</label>
              <Input
                placeholder="e.g. create, update, delete"
                value={actionFilter}
                onChange={(e) => setActionFilter(e.target.value)}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Logs ({filteredLogs.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {filteredLogs.length === 0 ? (
            <p className="text-center text-muted-foreground">No audit logs found.</p>
          ) : (
            <div className="space-y-3">
              {filteredLogs.map((log: AuditLog) => (
                <div key={log.id} className="flex items-start justify-between rounded-md border p-3">
                  <div>
                    <p className="font-medium">{log.action} on {log.resource_type}</p>
                    <p className="text-sm text-muted-foreground">
                      Resource ID: {log.resource_id || "N/A"} | User: {log.user_id || "System"}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(log.created_at).toLocaleString()}
                    </p>
                    {log.ip_address && (
                      <p className="text-xs text-muted-foreground">IP: {log.ip_address}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
