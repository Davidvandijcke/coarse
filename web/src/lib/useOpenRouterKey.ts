"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  beginLogin,
  clearStoredKey,
  completeLogin,
  loadStoredKey,
  saveStoredKey,
} from "./openrouterAuth";

/** sessionStorage key used to recover the review access token across the OAuth redirect. */
export const REVIEW_RETURN_TOKEN_KEY = "coarse.review_return_token";

export interface UseOpenRouterKey {
  apiKey: string;
  hasKey: boolean;
  /** Persist a pasted key, or clear it with "". */
  setKey: (key: string) => void;
  /** Begin OpenRouter OAuth, returning to the current URL (preserving ?token=). */
  startLogin: () => void;
  logout: () => void;
  /** Non-fatal status/error from the OAuth exchange. */
  notice: string | null;
}

/**
 * Tab-scoped OpenRouter key for the review page. Mirrors the home page's
 * handling (page.tsx): hydrate from sessionStorage and complete an OAuth
 * callback (?code=...) if present. Unlike the home page, it strips only the
 * ?code= param so the review's ?token= survives the round-trip.
 */
export function useOpenRouterKey(): UseOpenRouterKey {
  const [apiKey, setApiKey] = useState("");
  const [notice, setNotice] = useState<string | null>(null);
  const consumedRef = useRef(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get("code");
    const { key: stored, migratedFromLocalStorage } = loadStoredKey();

    if (migratedFromLocalStorage) {
      setNotice("Moved your saved OpenRouter key into tab-only storage; it clears when you close this tab.");
    }

    if (!code) {
      if (stored) setApiKey(stored);
      return;
    }
    if (consumedRef.current) return;
    consumedRef.current = true;

    // Strip ?code= but keep ?token= (and any other params) so the review stays
    // accessible and a reload can't replay a consumed code.
    params.delete("code");
    const qs = params.toString();
    window.history.replaceState({}, "", window.location.pathname + (qs ? `?${qs}` : ""));

    completeLogin(code)
      .then((key) => {
        setApiKey(key);
        setNotice(null);
        try {
          saveStoredKey(key);
        } catch {
          setNotice("Logged in, but couldn't keep the key in this tab.");
        }
      })
      .catch(() => {
        setNotice("OpenRouter login failed. Paste a key instead.");
        if (stored) setApiKey(stored);
      });
  }, []);

  const setKey = useCallback((key: string) => {
    const trimmed = key.trim();
    setApiKey(trimmed);
    if (trimmed) {
      try {
        saveStoredKey(trimmed);
      } catch {
        /* non-fatal */
      }
    } else {
      clearStoredKey();
    }
  }, []);

  const startLogin = useCallback(() => {
    // Login is a full-page redirect to OpenRouter and back. Pass the current URL
    // (including any ?token=) as the callback so OpenRouter returns here. The
    // review token is stashed per-review by ReviewPageClient, which recovers it
    // if OpenRouter drops ?token= from the URL on return.
    const callbackUrl = window.location.origin + window.location.pathname + window.location.search;
    beginLogin(callbackUrl).catch(() => {
      setNotice("OpenRouter login could not start. Paste a key instead.");
    });
  }, []);

  const logout = useCallback(() => {
    clearStoredKey();
    setApiKey("");
    setNotice(null);
  }, []);

  return {
    apiKey,
    hasKey: apiKey.trim().length > 0,
    setKey,
    startLogin,
    logout,
    notice,
  };
}
