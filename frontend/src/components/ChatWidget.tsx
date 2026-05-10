import { motion } from "framer-motion";
import { MessageCircle, Send, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { apiUrl } from "@/api/client";
import { cn } from "@/lib/utils";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

interface Props {
  sessionId: string;
}

export function ChatWidget({ sessionId }: Props) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "Я знаю ваши результаты — задайте любой вопрос о вашей карьере, специальностях или обучении.",
    },
  ]);
  const [draft, setDraft] = useState("");
  const [streaming, setStreaming] = useState(false);
  const scrollRef = useRef<HTMLDivElement | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, open]);

  const send = async () => {
    const text = draft.trim();
    if (!text || streaming) return;
    setDraft("");
    setStreaming(true);
    const next: ChatMessage[] = [...messages, { role: "user", content: text }, { role: "assistant", content: "" }];
    setMessages(next);

    const controller = new AbortController();
    abortRef.current = controller;
    try {
      const res = await fetch(apiUrl("/api/chat"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          messages: next.slice(0, -1).map((m) => ({ role: m.role, content: m.content })),
        }),
        signal: controller.signal,
      });
      if (!res.ok || !res.body) {
        throw new Error(`HTTP ${res.status}`);
      }
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        // SSE messages are separated by blank lines.
        const events = buffer.split("\n\n");
        buffer = events.pop() ?? "";
        for (const ev of events) {
          const lines = ev.split("\n");
          let event = "message";
          let data = "";
          for (const ln of lines) {
            if (ln.startsWith("event:")) event = ln.slice(6).trim();
            else if (ln.startsWith("data:")) data += ln.slice(5).trimStart();
          }
          if (event === "token" && data) {
            setMessages((prev) => {
              const copy = prev.slice();
              const last = copy[copy.length - 1];
              if (last && last.role === "assistant") {
                copy[copy.length - 1] = { ...last, content: last.content + data };
              }
              return copy;
            });
          }
          if (event === "done") {
            // No-op; the stream will end on its own.
          }
        }
      }
    } catch (e) {
      setMessages((prev) => {
        const copy = prev.slice();
        const last = copy[copy.length - 1];
        if (last && last.role === "assistant" && last.content.length === 0) {
          const err = e as { message?: string };
          copy[copy.length - 1] = { ...last, content: `Не удалось получить ответ: ${err.message ?? "ошибка"}` };
        }
        return copy;
      });
    } finally {
      setStreaming(false);
      abortRef.current = null;
    }
  };

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="fixed bottom-5 right-5 z-50 grid h-14 w-14 place-content-center rounded-full bg-gradient-to-br from-brand-700 to-accent-500 text-white shadow-lg hover:shadow-xl"
        aria-label={open ? "Закрыть чат" : "Открыть чат с ИИ-наставником"}
      >
        {open ? <X className="h-6 w-6" /> : <MessageCircle className="h-6 w-6" />}
      </button>
      {open && (
        <motion.div
          role="dialog"
          aria-label="Чат с ИИ-наставником"
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="fixed bottom-24 right-5 z-50 flex w-[min(92vw,380px)] flex-col rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-2xl"
        >
          <header className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 px-4 py-3">
            <div>
              <p className="text-sm font-semibold">ИИ-наставник</p>
              <p className="text-xs text-slate-500">Онлайн · знает ваш профиль</p>
            </div>
            <button onClick={() => setOpen(false)} className="btn-ghost p-1" aria-label="Закрыть">
              <X className="h-4 w-4" />
            </button>
          </header>
          <div ref={scrollRef} className="max-h-[60vh] flex-1 space-y-3 overflow-y-auto p-4">
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={cn(
                  "max-w-[85%] rounded-2xl px-3 py-2 text-sm",
                  m.role === "user"
                    ? "ml-auto bg-brand-700 text-white"
                    : "mr-auto bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-100",
                )}
              >
                {m.content || (m.role === "assistant" && streaming ? "…" : "")}
              </div>
            ))}
          </div>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              void send();
            }}
            className="flex items-center gap-2 border-t border-slate-200 dark:border-slate-800 p-3"
          >
            <input
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              placeholder="Спросите что-нибудь…"
              className="input py-2"
              aria-label="Сообщение"
              disabled={streaming}
            />
            <button
              type="submit"
              disabled={streaming || !draft.trim()}
              className="grid h-10 w-10 shrink-0 place-content-center rounded-xl bg-brand-700 text-white disabled:opacity-50"
              aria-label="Отправить"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        </motion.div>
      )}
    </>
  );
}
