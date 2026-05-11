import {
  DndContext,
  KeyboardSensor,
  PointerSensor,
  closestCenter,
  useSensor,
  useSensors,
  type DragEndEvent,
} from "@dnd-kit/core";
import {
  SortableContext,
  arrayMove,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { GripVertical } from "lucide-react";

import { cn } from "@/lib/utils";
import type { AnswerValue, Question } from "@/types";

interface Props {
  question: Question;
  index: number;
  value: AnswerValue | undefined;
  onChange: (v: AnswerValue) => void;
}

export function TestQuestion({ question, index, value, onChange }: Props) {
  return (
    <div className="card p-5 sm:p-6">
      <div className="mb-3 flex items-baseline gap-2 text-xs font-semibold uppercase tracking-wide text-brand-700 dark:text-brand-300">
        <span>Вопрос {index + 1}</span>
        <span className="text-slate-400">·</span>
        <span className="text-slate-500">
          {question.question_type === "scale"
            ? "оцените от 1 до 5"
            : question.question_type === "choice"
              ? "выберите вариант"
              : "расставьте по приоритету"}
        </span>
      </div>
      <p className="mb-5 text-base leading-relaxed text-slate-900 dark:text-slate-100">
        {question.text_ru}
      </p>
      {question.question_type === "scale" && (
        <ScaleInput value={typeof value === "number" ? value : undefined} onChange={onChange} options={question.options} />
      )}
      {question.question_type === "choice" && (
        <ChoiceInput value={typeof value === "string" ? value : undefined} onChange={onChange} options={question.options} />
      )}
      {question.question_type === "ranking" && (
        <RankingInput value={Array.isArray(value) ? (value as string[]) : undefined} onChange={onChange} options={question.options} />
      )}
    </div>
  );
}

// --------------------------------- scale ---------------------------------

function ScaleInput({
  value,
  onChange,
  options,
}: {
  value: number | undefined;
  onChange: (v: AnswerValue) => void;
  options: Record<string, unknown> | null;
}) {
  const min = (options?.min as number | undefined) ?? 1;
  const max = (options?.max as number | undefined) ?? 5;
  const minLabel = (options?.min_label as string | undefined) ?? "Совсем не про меня";
  const maxLabel = (options?.max_label as string | undefined) ?? "Полностью про меня";
  const values = Array.from({ length: max - min + 1 }, (_, i) => min + i);

  return (
    <div>
      <div role="radiogroup" aria-label="Шкала ответа" className="grid grid-cols-5 gap-2 sm:gap-3">
        {values.map((v) => {
          const selected = value === v;
          return (
            <button
              key={v}
              type="button"
              role="radio"
              aria-checked={selected}
              onClick={() => onChange(v)}
              className={cn(
                "h-12 rounded-xl border-2 text-base font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500",
                selected
                  ? "border-brand-700 bg-brand-700 text-white shadow"
                  : "border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-200 hover:border-brand-400",
              )}
            >
              {v}
            </button>
          );
        })}
      </div>
      <div className="mt-2 flex items-center justify-between text-xs text-slate-500">
        <span>{minLabel}</span>
        <span>{maxLabel}</span>
      </div>
    </div>
  );
}

// --------------------------------- choice --------------------------------

function ChoiceInput({
  value,
  onChange,
  options,
}: {
  value: string | undefined;
  onChange: (v: AnswerValue) => void;
  options: Record<string, unknown> | null;
}) {
  const items = (options?.options as Array<{ key: string; label: string }> | undefined) ?? [];
  return (
    <div role="radiogroup" aria-label="Варианты ответа" className="grid gap-2 sm:grid-cols-2">
      {items.map((it) => {
        const selected = value === it.key;
        return (
          <button
            key={it.key}
            type="button"
            role="radio"
            aria-checked={selected}
            onClick={() => onChange(it.key)}
            className={cn(
              "rounded-2xl border-2 px-4 py-4 text-left text-sm font-medium transition",
              selected
                ? "border-brand-700 bg-brand-50 text-brand-900 dark:bg-brand-900/30 dark:text-brand-100"
                : "border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 hover:border-brand-400",
            )}
          >
            {it.label}
          </button>
        );
      })}
    </div>
  );
}

// --------------------------------- ranking -------------------------------

function RankingInput({
  value,
  onChange,
  options,
}: {
  value: string[] | undefined;
  onChange: (v: AnswerValue) => void;
  options: Record<string, unknown> | null;
}) {
  const items = (options?.items as Array<{ key: string; label: string }> | undefined) ?? [];
  // Initial ordering: respect previous answer, fall back to seed order.
  const ordered = value && value.length === items.length
    ? items.slice().sort((a, b) => value.indexOf(a.key) - value.indexOf(b.key))
    : items;

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 4 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over || active.id === over.id) return;
    const fromIdx = ordered.findIndex((i) => i.key === active.id);
    const toIdx = ordered.findIndex((i) => i.key === over.id);
    if (fromIdx === -1 || toIdx === -1) return;
    const next = arrayMove(ordered, fromIdx, toIdx).map((i) => i.key);
    onChange(next);
  };

  // Initialize the answer if user hasn't touched it yet so the next button can enable.
  if (!value) {
    queueMicrotask(() => onChange(items.map((i) => i.key)));
  }

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <SortableContext items={ordered.map((i) => i.key)} strategy={verticalListSortingStrategy}>
        <ol className="space-y-2">
          {ordered.map((item, idx) => (
            <SortableItem key={item.key} id={item.key} label={item.label} rank={idx + 1} />
          ))}
        </ol>
      </SortableContext>
    </DndContext>
  );
}

function SortableItem({ id, label, rank }: { id: string; label: string; rank: number }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id });
  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };
  return (
    <li
      ref={setNodeRef}
      style={style}
      className={cn(
        "flex items-center gap-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-3 shadow-sm",
        isDragging && "opacity-70",
      )}
    >
      <span className="grid h-8 w-8 place-content-center rounded-lg bg-brand-50 dark:bg-brand-900/40 text-sm font-bold text-brand-800 dark:text-brand-200">
        {rank}
      </span>
      <span className="flex-1 text-sm text-slate-800 dark:text-slate-100">{label}</span>
      <button
        type="button"
        className="cursor-grab touch-none rounded-md p-1 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
        aria-label="Перетащить"
        {...attributes}
        {...listeners}
      >
        <GripVertical className="h-5 w-5" />
      </button>
    </li>
  );
}
