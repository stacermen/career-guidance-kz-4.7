import { motion } from "framer-motion";

import { cn } from "@/lib/utils";

interface Props {
  value: number;
  className?: string;
}

export function ProgressBar({ value, className }: Props) {
  const v = Math.max(0, Math.min(100, value));
  return (
    <div
      role="progressbar"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={Math.round(v)}
      className={cn(
        "h-2 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800",
        className,
      )}
    >
      <motion.div
        className="h-full rounded-full bg-gradient-to-r from-brand-700 to-accent-500"
        initial={false}
        animate={{ width: `${v}%` }}
        transition={{ type: "spring", stiffness: 80, damping: 18 }}
      />
    </div>
  );
}
