"use client";

import { useState, useCallback, useMemo } from "react";

export type CommentStatus = "active" | "done" | "dismissed";
export type CommentFilter = "all" | "active" | "done" | "dismissed";

function storageKey(reviewId: string) {
  return `coarse-status-${reviewId}`;
}

function filterKey(reviewId: string) {
  return `coarse-filter-${reviewId}`;
}

function loadStatuses(reviewId: string): Record<number, CommentStatus> {
  if (typeof window === "undefined") return {};
  try {
    const raw = localStorage.getItem(storageKey(reviewId));
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

function loadFilter(reviewId: string): CommentFilter {
  if (typeof window === "undefined") return "all";
  try {
    const raw = localStorage.getItem(filterKey(reviewId));
    if (raw === "active" || raw === "done" || raw === "dismissed") return raw;
    return "all";
  } catch {
    return "all";
  }
}

export function useCommentStatus(reviewId: string, commentCount: number) {
  const [statuses, setStatuses] = useState<Record<number, CommentStatus>>(
    () => loadStatuses(reviewId)
  );
  const [filter, setFilterState] = useState<CommentFilter>(
    () => loadFilter(reviewId)
  );

  const setStatus = useCallback(
    (commentNumber: number, status: CommentStatus) => {
      setStatuses((prev) => {
        const next = { ...prev, [commentNumber]: status };
        try {
          localStorage.setItem(storageKey(reviewId), JSON.stringify(next));
        } catch {
          // localStorage full — ignore
        }
        return next;
      });
    },
    [reviewId]
  );

  const setFilter = useCallback(
    (f: CommentFilter) => {
      setFilterState(f);
      try {
        localStorage.setItem(filterKey(reviewId), f);
      } catch {
        // ignore
      }
    },
    [reviewId]
  );

  const getStatus = useCallback(
    (commentNumber: number): CommentStatus => statuses[commentNumber] ?? "active",
    [statuses]
  );

  const remaining = useMemo(() => {
    let count = 0;
    for (let i = 1; i <= commentCount; i++) {
      if ((statuses[i] ?? "active") === "active") count++;
    }
    return count;
  }, [statuses, commentCount]);

  return { statuses, getStatus, setStatus, remaining, filter, setFilter };
}
