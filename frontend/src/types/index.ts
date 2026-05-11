export type QuestionType = "scale" | "choice" | "ranking";

export interface Question {
  id: number;
  order_num: number;
  text_ru: string;
  question_type: QuestionType;
  options: Record<string, unknown> | null;
}

export interface TestModule {
  id: number;
  slug: string;
  title_ru: string;
  title_en: string;
  description_ru: string;
  category: string;
  order_num: number;
  questions: Question[];
}

export interface SessionInfo {
  session_id: string;
  name: string | null;
  age: number | null;
  education_level: string | null;
}

export interface University {
  id: number;
  name_ru: string;
  name_en: string;
  short_name: string | null;
  city: string;
  website: string | null;
  logo_url: string | null;
}

export interface Specialization {
  id: number;
  code: string;
  name_ru: string;
  name_en: string;
  description_ru: string;
  category: string;
  grant_available: boolean;
  tuition_cost: number;
  university: University;
}

export interface CareerPath {
  title_ru: string;
  match_score: number;
  why_match: string;
  specialization_categories: string[];
}

export interface AIAnalysis {
  personality_summary: string;
  strengths: string[];
  growth_areas: string[];
  ideal_work_environment: string;
  career_paths: CareerPath[];
  study_tips: string;
  motivational_message: string;
}

export interface Recommendation {
  id: number;
  match_score: number;
  reason_ru: string;
  rank: number;
  specialization: Specialization;
}

export interface ResultsResponse {
  session_id: string;
  created_at: string;
  raw_scores: Record<string, Record<string, number>>;
  traits: Record<string, unknown> | null;
  analysis: AIAnalysis;
  recommendations: Recommendation[];
}

export type AnswerValue = number | string | number[] | string[];

export interface AnswerLocal {
  question_id: number;
  value: AnswerValue;
}

export const CITY_OPTIONS = [
  "Алматы",
  "Астана",
  "Шымкент",
  "Қарағанды",
  "Павлодар",
  "Өскемен",
  "Семей",
  "Қостанай",
  "Петропавл",
  "Көкшетау",
  "Орал",
  "Ақтөбе",
  "Ақтау",
  "Атырау",
  "Қызылорда",
  "Тараз",
  "Талдыкорган",
  "Туркестан",
] as const;
export const CATEGORY_OPTIONS = [
  "IT",
  "Engineering",
  "Medicine",
  "Economics",
  "Law",
  "Pedagogy",
  "Arts",
] as const;

export const CATEGORY_LABEL_RU: Record<(typeof CATEGORY_OPTIONS)[number], string> = {
  IT: "ИТ",
  Engineering: "Инженерия",
  Medicine: "Медицина",
  Economics: "Экономика",
  Law: "Право",
  Pedagogy: "Педагогика",
  Arts: "Искусство и медиа",
};
