import { useEffect, useState } from "react";

import { fetchResults } from "@/api/endpoints";
import type { ResultsResponse } from "@/types";

export function useResults(sessionId: string | undefined) {
  const [data, setData] = useState<ResultsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(Boolean(sessionId));
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) return;
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchResults(sessionId)
      .then((r) => {
        if (!cancelled) setData(r);
      })
      .catch((e) => {
        if (!cancelled) setError(e?.response?.data?.detail ?? e?.message ?? "Ошибка загрузки");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  return { data, loading, error };
}
