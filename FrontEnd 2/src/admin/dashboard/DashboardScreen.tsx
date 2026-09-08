import { useState, useMemo } from "react";
import type { Category } from "../../types";
import { PARTICIPANTS, PARTICIPATIONS, CATEGORY_LABELS } from "../../data/mockData";
import { Avatar, StatusBadge, CategoryBadge, StreakBadge, KPICard } from "../../components/common/Primitives";
import { IconUsers, IconBook, IconStar, IconFire, IconWarn } from "../../components/icons/Icons";

export function DashboardScreen() {
  const [catFilter, setCatFilter] = useState<Category | "all">("all");

  const filtered = useMemo(
    () =>
      catFilter === "all"
        ? PARTICIPATIONS
        : PARTICIPATIONS.filter((p) => p.category === catFilter),
    [catFilter]
  );

  const topStreaks = [...PARTICIPANTS]
    .sort((a, b) => b.streak - a.streak)
    .slice(0, 8);

  const atRiskCount = PARTICIPANTS.filter(
    (p) => !p.answeredToday && p.streak > 4
  ).length;

  return (
    <div className="p-7 space-y-6 min-h-full">
      {/* Page header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-[1.65rem] font-bold text-stone-900 font-display leading-tight">
            Panel de Control
          </h1>
          <p className="text-sm text-stone-400 mt-0.5">
            Lunes, 8 de septiembre de 2026 · Día 251 del año
          </p>
        </div>
        <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-2">
          <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
          <span className="text-xs font-medium text-emerald-700">
            Bot activo
          </span>
        </div>
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-4 gap-4">
        <KPICard
          label="Participantes activos"
          value="47"
          sub="grupo Modo Íntegro"
          icon={<IconUsers />}
        />
        <KPICard
          label="Respondieron hoy"
          value="31 / 47"
          sub="lectura del día registrada"
          icon={<IconBook />}
        />
        <KPICard
          label="Promedio pts. semana"
          value="84 pts"
          sub="↑ 12 % vs semana anterior"
          icon={<IconStar />}
          accent
        />
        <KPICard
          label="Racha más larga activa"
          value="31 días"
          sub="Patricia Reyes 🔥"
          icon={<IconFire />}
          accent
        />
      </div>

      {/* Two-column layout */}
      <div className="grid grid-cols-5 gap-5">
        {/* LEFT: Recent participations */}
        <div className="col-span-3 bg-white rounded-xl border border-stone-200 shadow-sm overflow-hidden flex flex-col">
          <div className="px-5 py-4 border-b border-stone-100 flex items-center justify-between flex-shrink-0">
            <div>
              <h2 className="text-sm font-semibold text-stone-900">
                Últimas participaciones
              </h2>
              <p className="text-xs text-stone-400 mt-0.5">
                Actualizado hace 2 min
              </p>
            </div>
            <select
              value={catFilter}
              onChange={(e) =>
                setCatFilter(e.target.value as Category | "all")
              }
              className="text-xs border border-stone-200 rounded-lg px-2.5 py-1.5 bg-white text-stone-600 focus:outline-none focus:ring-2 focus:ring-amber-400 cursor-pointer"
            >
              <option value="all">Todas las categorías</option>
              {(Object.keys(CATEGORY_LABELS) as Category[]).map((k) => (
                <option key={k} value={k}>
                  {CATEGORY_LABELS[k]}
                </option>
              ))}
            </select>
          </div>

          <div className="overflow-auto flex-1" style={{ maxHeight: 420 }}>
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-stone-50 border-b border-stone-100">
                <tr>
                  <th className="text-left px-5 py-2.5 text-[11px] font-semibold text-stone-400 uppercase tracking-wider">
                    Participante
                  </th>
                  <th className="text-left px-3 py-2.5 text-[11px] font-semibold text-stone-400 uppercase tracking-wider">
                    Categoría
                  </th>
                  <th className="text-right px-3 py-2.5 text-[11px] font-semibold text-stone-400 uppercase tracking-wider">
                    Pts
                  </th>
                  <th className="text-right px-3 py-2.5 text-[11px] font-semibold text-stone-400 uppercase tracking-wider">
                    Hora
                  </th>
                  <th className="text-right px-5 py-2.5 text-[11px] font-semibold text-stone-400 uppercase tracking-wider">
                    Estado
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-50">
                {filtered.map((p) => (
                  <tr
                    key={p.id}
                    className="hover:bg-stone-50/70 transition-colors group"
                  >
                    <td className="px-5 py-3">
                      <div className="flex items-center gap-2.5">
                        <Avatar initials={p.initials} />
                        <div>
                          <p className="font-medium text-stone-800 text-sm leading-tight">
                            {p.name}
                          </p>
                          <p className="text-[11px] text-stone-400 font-mono mt-0.5">
                            {p.phone}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="px-3 py-3">
                      <CategoryBadge category={p.category} />
                    </td>
                    <td className="px-3 py-3 text-right">
                      <span
                        className={`font-mono font-semibold text-sm ${p.points > 0 ? "text-stone-800" : "text-stone-300"}`}
                      >
                        {p.points > 0 ? `+${p.points}` : "—"}
                      </span>
                    </td>
                    <td className="px-3 py-3 text-right">
                      <span className="text-[11px] text-stone-400 font-mono">
                        {p.time}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-right">
                      <StatusBadge status={p.status} />
                    </td>
                  </tr>
                ))}
                {filtered.length === 0 && (
                  <tr>
                    <td
                      colSpan={5}
                      className="px-5 py-10 text-center text-sm text-stone-400"
                    >
                      Sin participaciones para esta categoría
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* RIGHT: Top Streaks */}
        <div className="col-span-2 bg-white rounded-xl border border-stone-200 shadow-sm overflow-hidden flex flex-col">
          <div className="px-5 py-4 border-b border-stone-100 flex-shrink-0">
            <h2 className="text-sm font-semibold text-stone-900">
              Top Rachas
            </h2>
            <p className="text-xs text-stone-400 mt-0.5">
              Ranking de constancia
            </p>
          </div>

          <div className="divide-y divide-stone-50 flex-1 overflow-auto">
            {topStreaks.map((p, i) => {
              const atRisk = !p.answeredToday && p.streak > 4;
              const medals = ["🥇", "🥈", "🥉"];
              return (
                <div
                  key={p.id}
                  className={`px-5 py-3 flex items-center gap-3 transition-colors ${atRisk ? "bg-orange-50/70 border-l-2 border-orange-400" : "hover:bg-stone-50/70"}`}
                >
                  <span className="w-7 text-center text-sm flex-shrink-0">
                    {i < 3 ? (
                      medals[i]
                    ) : (
                      <span className="font-mono text-stone-300 text-xs font-bold">
                        {i + 1}
                      </span>
                    )}
                  </span>
                  <Avatar initials={p.initials} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1.5">
                      <p className="text-sm font-medium text-stone-800 truncate">
                        {p.name}
                      </p>
                      {atRisk && (
                        <span
                          className="text-orange-500 flex-shrink-0"
                          title="Racha en riesgo de romperse hoy"
                        >
                          <IconWarn />
                        </span>
                      )}
                    </div>
                    <p className="text-[11px] text-stone-400">
                      Máx:{" "}
                      <span className="font-mono font-medium">
                        {p.maxStreak}d
                      </span>
                    </p>
                  </div>
                  <StreakBadge days={p.streak} atRisk={atRisk} />
                </div>
              );
            })}
          </div>

          {atRiskCount > 0 && (
            <div className="px-5 py-3 border-t border-stone-100 bg-orange-50/60 flex-shrink-0">
              <p className="text-xs text-orange-700 font-medium text-center">
                ⚠ {atRiskCount} participante
                {atRiskCount > 1 ? "s" : ""} en riesgo de perder racha hoy
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
