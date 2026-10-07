"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, useRef } from "react";
import { useToast } from "@/providers/toast-provider";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Spinner } from "@/components/loading";
import { getFiles, uploadFile, downloadFile, deleteFile } from "@/services/files";
import type { File } from "@/types/api";

export default function FilesPage() {
  const queryClient = useQueryClient();
  const { addToast } = useToast();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);

  const { data: files, isLoading } = useQuery({
    queryKey: ["files"],
    queryFn: getFiles,
  });

  const uploadMutation = useMutation({
    mutationFn: async (file: globalThis.File) => {
      return uploadFile(file);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["files"] });
      addToast("File uploaded successfully", "success");
      const input = document.getElementById("file-upload") as HTMLInputElement | null;
      if (input) {
        input.value = "";
      }
    },
    onError: () => {
      addToast("Failed to upload file", "error");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      await deleteFile(id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["files"] });
      addToast("File deleted", "success");
      setConfirmDeleteId(null);
      if (selectedFile?.id === confirmDeleteId) {
        setSelectedFile(null);
      }
    },
    onError: () => {
      addToast("Failed to delete file", "error");
    },
  });

  const handleUpload = (e: React.FormEvent) => {
    e.preventDefault();
    const input = document.getElementById("file-upload") as HTMLInputElement | null;
    if (input?.files?.[0]) {
      uploadMutation.mutate(input.files[0]);
    }
  };

  const handleDownload = async (file: File) => {
    try {
      const blob = await downloadFile(file.id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = file.original_filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch {
      addToast("Failed to download file", "error");
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  if (isLoading) {
    return <Spinner size="lg" />;
  }

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Files</h1>
        <p className="mt-1 text-muted-foreground">Upload and manage your files</p>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Upload File</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleUpload} className="flex items-center gap-4">
            <Input
              id="file-upload"
              type="file"
              disabled={uploadMutation.isPending}
              className="flex-1"
            />
            <Button type="submit" disabled={uploadMutation.isPending}>
              {uploadMutation.isPending ? "Uploading..." : "Upload"}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Your Files ({files?.length || 0})</CardTitle>
        </CardHeader>
        <CardContent>
          {files?.length === 0 ? (
            <p className="text-center text-muted-foreground">No files uploaded yet.</p>
          ) : (
            <div className="space-y-3">
              {files?.map((file: File) => (
                <div key={file.id} className={`flex items-center justify-between rounded-md border p-3 ${selectedFile?.id === file.id ? "border-primary bg-primary/5" : ""}`}>
                  <div className="flex-1">
                    <p className="font-medium">{file.original_filename}</p>
                    <p className="text-sm text-muted-foreground">
                      {formatSize(file.file_size)} | {file.mime_type}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Uploaded: {new Date(file.created_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDownload(file)}
                    >
                      Download
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      disabled={deleteMutation.isPending && confirmDeleteId === file.id}
                      onClick={() => setConfirmDeleteId(file.id)}
                    >
                      Delete
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {confirmDeleteId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Confirm Delete</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                Are you sure you want to delete this file? This action cannot be undone.
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
