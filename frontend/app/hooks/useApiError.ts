"use client";

import { useMutation } from "@tanstack/react-query";
import axios from "axios";
import { apiClient } from "@/lib/api";
import { useToast } from "@/providers/toast-provider";

export function useApiError() {
  const { addToast } = useToast();

  return useMutation({
    mutationFn: async (fn: () => Promise<any>) => {
      try {
        return await fn();
      } catch (error) {
        const message = getApiErrorMessage(error);
        addToast(message, "error");
        throw error;
      }
    },
  });
}

function getApiErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const axiosError = error as any;
    if (axiosError.response?.data) {
      const data = axiosError.response.data;
      if (data?.error?.message) {
        return data.error.message;
      }
      if (typeof data === "string") {
        return data;
      }
      if (typeof data.detail === "string") {
        return data.detail;
      }
    }
    if (axiosError.response?.status === 401) {
      return "Unauthorized. Please log in again.";
    }
    if (axiosError.response?.status === 403) {
      return "You don't have permission to perform this action.";
    }
    if (axiosError.response?.status === 404) {
      return "Resource not found.";
    }
    if (axiosError.response?.status === 409) {
      return "A conflict occurred. Please try again.";
    }
    if (axiosError.response?.status === 422) {
      return "Invalid data provided.";
    }
    if (axiosError.response?.status === 429) {
      return "Too many requests. Please try again later.";
    }
    if (axiosError.response?.status === 500) {
      return "Server error. Please try again later.";
    }
    if (axiosError.message === "Network Error") {
      return "Network error. Please check your connection.";
    }
    return axiosError.message || "An unexpected error occurred.";
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "An unexpected error occurred.";
}
