interface ProbabilityBarProps {
  label: string;
  value: number;
  color: string;
  highlight?: boolean;
}

export function ProbabilityBar({ label, value, color, highlight }: ProbabilityBarProps) {
  const pct = Math.round(value * 100);
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className={highlight ? 'font-semibold text-white' : 'text-slate-400'}>{label}</span>
        <span className={highlight ? 'font-bold text-white' : 'text-slate-300'}>{pct}%</span>
      </div>
      <div className="h-2.5 rounded-full bg-slate-700/80 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
