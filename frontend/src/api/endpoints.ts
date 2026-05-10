import type {
  AIAnalysis,
  AnswerLocal,
  ResultsResponse,
  SessionInfo,
  Specialization,
  TestModule,
  University,
} from "@/types";

import { http } from "./client";

export async function createSession(payload: {
  name?: string | null;
  age?: number | null;
  education_level?: string | null;
}): Promise<SessionInfo> {
  const { data } = await http.post<SessionInfo>("/api/session", payload);
  return data;
}

export async function fetchTests(): Promise<TestModule[]> {
  const { data } = await http.get<TestModule[]>("/api/tests");
  return data;
}

export async function saveAnswers(payload: {
  session_id: string;
  answers: AnswerLocal[];
}): Promise<{ saved: number }> {
  const { data } = await http.post<{ saved: number }>("/api/answers", payload);
  return data;
}

export async function analyze(session_id: string): Promise<ResultsResponse> {
  const { data } = await http.post<ResultsResponse>("/api/analyze", { session_id });
  return data;
}

export async function fetchResults(session_id: string): Promise<ResultsResponse> {
  const { data } = await http.get<ResultsResponse>(`/api/results/${session_id}`);
  return data;
}

export function resultsPdfUrl(session_id: string): string {
  return `${http.defaults.baseURL ?? ""}/api/results/${session_id}/pdf`;
}

export async function fetchUniversities(city?: string | null): Promise<{ items: University[] }> {
  const { data } = await http.get<{ items: University[] }>("/api/universities", {
    params: { city: city ?? undefined },
  });
  return data;
}

export async function fetchSpecializations(params: {
  city?: string | null;
  category?: string | null;
  university_id?: number | null;
}): Promise<{ items: Specialization[] }> {
  const { data } = await http.get<{ items: Specialization[] }>("/api/specializations", {
    params: {
      city: params.city ?? undefined,
      category: params.category ?? undefined,
      university_id: params.university_id ?? undefined,
    },
  });
  return data;
}

// Re-export for components.
export type { AIAnalysis };
