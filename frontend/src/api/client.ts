import axios from "axios";

// Base URL is read at build time. In production behind nginx we want
// same-origin requests so the path remains `/api/...`.
export const API_BASE = (import.meta.env.VITE_API_URL ?? "").replace(/\/$/, "");

export const http = axios.create({
  baseURL: API_BASE || undefined,
  timeout: 60_000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Helper to build absolute URL for SSE endpoints (EventSource doesn't share axios baseURL).
export function apiUrl(path: string): string {
  if (path.startsWith("http")) return path;
  return `${API_BASE}${path.startsWith("/") ? path : `/${path}`}`;
}
