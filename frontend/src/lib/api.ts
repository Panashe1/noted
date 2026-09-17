import type { components } from "@/types/api";

export type Album = components["schemas"]["AlbumOut"];
export type AlbumSearch = components["schemas"]["AlbumSearchResponse"];
export type User = components["schemas"]["UserPrivate"];
export type PublicUser = components["schemas"]["UserPublic"];
export type Health = components["schemas"]["HealthResponse"];
export type RegisterRequest = components["schemas"]["RegisterRequest"];
export type LoginRequest = components["schemas"]["LoginRequest"];

export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8001";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly detail: string,
  ) {
    super(detail);
    this.name = "ApiError";
  }
}

async function readDetail(res: Response): Promise<string> {
  try {
    const body = await res.json();
    if (typeof body?.detail === "string") return body.detail;
    if (body?.detail) return JSON.stringify(body.detail);
  } catch {
    // fall through to status text
  }
  return res.statusText || `Request failed (${res.status})`;
}

async function request<T>(path: string, init: RequestInit = {}, allowRefresh = true): Promise<T> {
  const res = await fetch(`${API_URL}/api/v1${path}`, {
    ...init,
    credentials: "include",
    headers: { "Content-Type": "application/json", ...(init.headers ?? {}) },
  });

  // Access token expired: try one silent refresh, then retry the original call.
  if (res.status === 401 && allowRefresh && !path.startsWith("/auth/")) {
    const refreshed = await fetch(`${API_URL}/api/v1/auth/refresh`, {
      method: "POST",
      credentials: "include",
    });
    if (refreshed.ok) return request<T>(path, init, false);
  }

  if (!res.ok) throw new ApiError(res.status, await readDetail(res));
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  health: () => request<Health>("/health", { cache: "no-store" }),

  searchAlbums: (q: string, limit = 20) =>
    request<AlbumSearch>(`/albums/search?${new URLSearchParams({ q, limit: String(limit) })}`),
  album: (id: string, init?: RequestInit) => request<Album>(`/albums/${id}`, init),

  me: () => request<User>("/users/me"),
  user: (username: string, init?: RequestInit) =>
    request<PublicUser>(`/users/${encodeURIComponent(username)}`, init),

  register: (body: RegisterRequest) =>
    request<User>("/auth/register", { method: "POST", body: JSON.stringify(body) }),
  login: (body: LoginRequest) =>
    request<User>("/auth/login", { method: "POST", body: JSON.stringify(body) }),
  logout: () => request<void>("/auth/logout", { method: "POST" }),
};
