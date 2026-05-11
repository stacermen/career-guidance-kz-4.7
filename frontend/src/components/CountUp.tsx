import { animate } from "framer-motion";
import { useEffect, useRef, useState } from "react";

interface Props {
  to: number;
  duration?: number;
  format?: (n: number) => string;
}

export function CountUp({ to, duration = 1.1, format = (n) => `${Math.round(n)}` }: Props) {
  const [val, setVal] = useState(0);
  const startedRef = useRef(false);
  useEffect(() => {
    if (startedRef.current) return;
    startedRef.current = true;
    const controls = animate(0, to, {
      duration,
      ease: "easeOut",
      onUpdate: (v) => setVal(v),
    });
    return () => controls.stop();
  }, [to, duration]);
  return <span>{format(val)}</span>;
}
