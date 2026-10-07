"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useToast } from "@/providers/toast-provider";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Spinner } from "@/components/loading";
import { getTasks, createTask, deleteTask } from "@/services/tasks";
import type { Task } from "@/types/api";

const STATUS_COLORS: Record<string, string> = {
  TODO: "bg-gray-100 text-gray-800",
  IN_PROGRESS: "bg-blue-100 text-blue-800",
  REVIEW: "bg-yellow-100 text-yellow-800",
  DONE: "bg-green-100 text-green-800",
};

const PRIORITY_COLORS: Record<string, string> = {
  LOW: "bg-gray-100 text-gray-800",
  MEDIUM: "bg-blue-100 text-blue-800",
  HIGH: "bg-orange-100 text-orange-800",
  URGENT: "bg-red-100 text-red-800",
};

export default function TasksPage() {
  const queryClient = useQueryClient();
  const { addToast } = useToast();
  const [showCreate, setShowCreate] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState("TODO");
  const [priority, setPriority] = useState("MEDIUM");
  const [projectId, setProjectId] = useState("");
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);

  const { data: tasks, isLoading } = useQuery({
    queryKey: ["tasks"],
    queryFn: getTasks,
  });

  const createMutation = useMutation({
    mutationFn: async (data: { title: string; description?: string; status: string; priority: string; project_id: string }) => {
      const response = await createTask(data);
      return response;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      addToast("Task created successfully", "success");
      setShowCreate(false);
      setTitle("");
      setDescription("");
      setStatus("TODO");
      setPriority("MEDIUM");
      setProjectId("");
    },
    onError: () => {
      addToast("Failed to create task", "error");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      await deleteTask(id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      addToast("Task deleted", "success");
      setConfirmDeleteId(null);
    },
    onError: () => {
      addToast("Failed to delete task", "error");
    },
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate({ title, description: description || undefined, status, priority, project_id: projectId });
  };

  if (isLoading) {
    return <Spinner size="lg" />;
  }

  return (
    <div className="p-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Tasks</h1>
          <p className="mt-1 text-muted-foreground">Manage your tasks</p>
        </div>
        <Button onClick={() => setShowCreate(!showCreate)}>
          {showCreate ? "Cancel" : "Create Task"}
        </Button>
      </div>

      {showCreate && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Create Task</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Title</label>
                <Input
                  placeholder="Task title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  disabled={createMutation.isPending}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Description</label>
                <Input
                  placeholder="Optional description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  disabled={createMutation.isPending}
                />
              </div>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Status</label>
                  <select
                    value={status}
                    onChange={(e) => setStatus(e.target.value)}
                    disabled={createMutation.isPending}
                    className="rounded-md border border-input bg-background px-3 py-2 text-sm"
                  >
                    <option value="TODO">Todo</option>
                    <option value="IN_PROGRESS">In Progress</option>
                    <option value="REVIEW">Review</option>
                    <option value="DONE">Done</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Priority</label>
                  <select
                    value={priority}
                    onChange={(e) => setPriority(e.target.value)}
                    disabled={createMutation.isPending}
                    className="rounded-md border border-input bg-background px-3 py-2 text-sm"
                  >
                    <option value="LOW">Low</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HIGH">High</option>
                    <option value="URGENT">Urgent</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Project ID</label>
                  <Input
                    placeholder="Project ID"
                    value={projectId}
                    onChange={(e) => setProjectId(e.target.value)}
                    disabled={createMutation.isPending}
                  />
                </div>
              </div>
              <Button type="submit" disabled={createMutation.isPending}>
                {createMutation.isPending ? "Creating..." : "Create"}
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {tasks?.map((task: Task) => (
          <Card key={task.id}>
            <CardHeader>
              <CardTitle className="text-lg">{task.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-3">{task.description || "No description"}</p>
              <div className="flex flex-wrap gap-2 mb-3">
                <span className={`rounded-full px-3 py-1 text-xs font-medium ${STATUS_COLORS[task.status] || "bg-secondary"}`}>
                  {task.status}
                </span>
                <span className={`rounded-full px-3 py-1 text-xs font-medium ${PRIORITY_COLORS[task.priority] || "bg-secondary"}`}>
                  {task.priority}
                </span>
              </div>
              <p className="text-xs text-muted-foreground mb-3">Project: {task.project_id}</p>
              <Button
                variant="destructive"
                size="sm"
                disabled={deleteMutation.isPending && confirmDeleteId === task.id}
                onClick={() => setConfirmDeleteId(task.id)}
              >
                Delete
              </Button>
            </CardContent>
          </Card>
        ))}
        {tasks?.length === 0 && (
          <Card>
            <CardContent className="pt-6">
              <p className="text-center text-muted-foreground">No tasks yet. Create one to get started.</p>
            </CardContent>
          </Card>
        )}
      </div>

      {confirmDeleteId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Confirm Delete</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                Are you sure you want to delete this task? This action cannot be undone.
              </p>
              <div className="flex gap-3">
                <Button
                  variant="destructive"
                  onClick={() => deleteMutation.mutate(confirmDeleteId)}
                  disabled={deleteMutation.isPending}
                >
                  {deleteMutation.isPending ? "Deleting..." : "Delete"}
                </Button>
                <Button variant="outline" onClick={() => setConfirmDeleteId(null)}>
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
