import type { ReactNode } from "react";
import type { Status, Category } from "../../types";
import { CATEGORY_LABELS, CATEGORY_COLORS, AVATAR_COLORS } from "../../data/mockData";

export function Avatar({
  initials,
  size = "sm",
}: {
  initials: string;
  size?: "sm" | "md";
}) {
  const idx =
    (initials.charCodeAt(0) + (initials.charCodeAt(1) || 0)) %
    AVATAR_COLORS.length;
  return (
    <div
      className={`rounded-full flex items-center justify-center font-semibold flex-shrink-0 ${AVATAR_COLORS[idx]} ${size === "sm" ? "w-8 h-8 text-xs" : "w-10 h-10 text-sm"}`}
    >
      {initials}
    </div>
  );
}

export function StatusBadge({ status }: { status: Status }) {
  if (status === "valido")
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-700">
        ✓ Válido
      </span>
    );
  if (status === "invalido")
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700">
        ✕ Inválido
      </span>
    );
  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-stone-100 text-stone-500">
      ⏳ Pendiente
    </span>
  );
}

export function CategoryBadge({ category }: { category: Category }) {
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${CATEGORY_COLORS[category]}`}
    >
      {CATEGORY_LABELS[category]}
    </span>
  );
}

export function StreakBadge({
  days,
  atRisk = false,
}: {
  days: number;
  atRisk?: boolean;
}) {
  return (
    <span
      className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold ${atRisk ? "bg-orange-100 text-orange-700" : "bg-amber-100 text-amber-800"}`}
    >
      🔥 {days}d
    </span>
  );
}

export function KPICard({
  label,
  value,
  sub,
  icon,
  accent = false,
}: {
  label: string;
  value: string;
  sub?: string;
  icon: ReactNode;
  accent?: boolean;
}) {
  return (
    <div className="bg-white rounded-xl p-5 border border-stone-200 shadow-sm hover:shadow-md transition-shadow flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-stone-500 uppercase tracking-wide">
          {label}
        </span>
        <span
          className={`p-2 rounded-lg ${accent ? "bg-amber-100 text-amber-600" : "bg-stone-100 text-stone-500"}`}
        >
          {icon}
        </span>
      </div>
      <div>
        <p className="text-2xl font-bold text-stone-900 font-mono leading-none">
          {value}
        </p>
        {sub && <p className="text-xs text-stone-400 mt-1.5">{sub}</p>}
      </div>
    </div>
  );
}
