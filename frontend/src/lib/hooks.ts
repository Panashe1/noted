"use client";

import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { api, ApiError, type Review as ReviewType, type ReviewWrite, type User } from "./api";

export const meKey = ["me"] as const;

export function useMe() {
  return useQuery<User | null>({
    queryKey: meKey,
    queryFn: async () => {
      try {
        return await api.me();
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) return null;
        throw err;
      }
    },
    staleTime: 5 * 60 * 1000,
    retry: false,
  });
}

export function useLogout() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.logout,
    onSuccess: () => queryClient.setQueryData(meKey, null),
  });
}

export function useAlbumSearch(query: string) {
  const q = query.trim();
  return useQuery({
    queryKey: ["albums", "search", q],
    queryFn: () => api.searchAlbums(q),
    enabled: q.length >= 2,
    staleTime: 60 * 1000,
    placeholderData: keepPreviousData,
  });
}

export function useDebouncedValue<T>(value: T, delayMs = 300): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const handle = setTimeout(() => setDebounced(value), delayMs);
    return () => clearTimeout(handle);
  }, [value, delayMs]);
  return debounced;
}

export const albumReviewsKey = (albumId: string) => ["reviews", "album", albumId] as const;
export const myReviewKey = (albumId: string) => ["reviews", "mine", albumId] as const;

export function useAlbumReviews(albumId: string, limit: number, offset: number) {
  return useQuery({
    queryKey: [...albumReviewsKey(albumId), limit, offset],
    queryFn: () => api.albumReviews(albumId, limit, offset),
    placeholderData: keepPreviousData,
  });
}

/** The signed-in user's own review of this album, or null when they have not written one. */
export function useMyReview(albumId: string, enabled: boolean) {
  return useQuery<ReviewType | null>({
    queryKey: myReviewKey(albumId),
    queryFn: async () => {
      try {
        return await api.myReview(albumId);
      } catch (err) {
        if (err instanceof ApiError && (err.status === 404 || err.status === 401)) return null;
        throw err;
      }
    },
    enabled,
    retry: false,
  });
}

/** Refresh everything a review touches: the list, your own copy, and the server-rendered
 *  album aggregate at the top of the page. */
function useReviewInvalidation(albumId: string) {
  const queryClient = useQueryClient();
  const router = useRouter();
  return async () => {
    await queryClient.invalidateQueries({ queryKey: albumReviewsKey(albumId) });
    await queryClient.invalidateQueries({ queryKey: myReviewKey(albumId) });
    router.refresh();
  };
}

export function useSaveReview(albumId: string) {
  const invalidate = useReviewInvalidation(albumId);
  return useMutation({
    mutationFn: (body: ReviewWrite) => api.saveReview(albumId, body),
    onSuccess: invalidate,
  });
}

export function useDeleteReview(albumId: string) {
  const invalidate = useReviewInvalidation(albumId);
  return useMutation({
    mutationFn: () => api.deleteReview(albumId),
    onSuccess: invalidate,
  });
}
