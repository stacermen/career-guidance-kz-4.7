import { useCallback } from "react";

import { createSession } from "@/api/endpoints";
import { useTestStore } from "@/stores/testStore";

export function useSession() {
  const session = useTestStore((s) => s.session);
  const setSession = useTestStore((s) => s.setSession);

  const start = useCallback(
    async (payload: { name?: string | null; age?: number | null; education_level?: string | null }) => {
      const info = await createSession(payload);
      setSession(info);
      return info;
    },
    [setSession],
  );

  return { session, start };
}
