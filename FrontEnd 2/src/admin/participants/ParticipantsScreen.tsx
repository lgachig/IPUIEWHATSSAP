import { useState } from "react";
import { PARTICIPANTS, PARTICIPATIONS } from "../../data/mockData";
import { Avatar, StatusBadge, CategoryBadge, StreakBadge } from "../../components/common/Primitives";
import { IconSearch, IconX } from "../../components/icons/Icons";

export function ParticipantsScreen() {
  const [search, setSearch] = useState("");
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const filtered = PARTICIPANTS.filter(
    (p) =>
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.phone.includes(search)
  );
  const selected = PARTICIPANTS.find((p) => p.id === selectedId) ?? null;

  return (
    <div className="p-7 flex flex-col gap-5 h-full">
      <div className="flex items-center justify-between flex-shrink-0">
        <div>
          <h1 className="text-[1.65rem] font-bold text-stone-900 font-display">
            Participantes
          </h1>
          <p className="text-sm text-stone-400 mt-0.5">
            {PARTICIPANTS.length} personas registradas en total
          </p>
        </div>
        <button className="px-4 py-2 text-sm font-medium bg-amber-500 text-white rounded-lg hover:bg-amber-600 transition-colors">
          + Agregar participante
        </button>
      </div>

      <div className="relative max-w-xs flex-shrink-0">
        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-stone-400">
          <IconSearch />
        </span>
        <input
          type="text"
          placeholder="Buscar nombre o teléfono…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-9 pr-4 py-2 text-sm border border-stone-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-amber-400"
        />
      </div>

      <div className="flex gap-4 flex-1 overflow-hidden">
        {/* Table */}
        <div className="flex-1 bg-white rounded-xl border border-stone-200 shadow-sm overflow-hidden">
          <div className="overflow-auto h-full">
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-stone-50 border-b border-stone-100">
                <tr>
                  <th className="text-left px-5 py-3 text-[11px] font-semibold text-stone-400 uppercase tracking-wider">
                    Nombre
                  </th>
                  <th className="text-left px-3 py-3 text-[11px] font-semibold text-stone-400 uppercase tracking-wider">
                    Teléfono
                  </th>
                  <th className="text-left px-3 py-3 text-[11px] font-semibold text-stone-400 uppercase tracking-wider">
                    Rol
                  </th>
                  <th className="text-right px-3 py-3 text-[11px] font-semibold text-stone-400 uppercase tracking-wider">
                    Comodines
                  </th>
                  <th className="text-right px-3 py-3 text-[11px] font-semibold text-stone-400 uppercase tracking-wider">
                    Puntos
                  </th>
                  <th className="text-right px-3 py-3 text-[11px] font-semibold text-stone-400 uppercase tracking-wider">
                    Racha
                  </th>
                  <th className="text-right px-5 py-3 text-[11px] font-semibold text-stone-400 uppercase tracking-wider">
                    Máx.
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-50">
                {filtered.map((p) => {
                  const atRisk = !p.answeredToday && p.streak > 4;
                  return (
                    <tr
                      key={p.id}
                      onClick={() =>
                        setSelectedId(p.id === selectedId ? null : p.id)
                      }
                      className={`cursor-pointer transition-colors ${selectedId === p.id ? "bg-amber-50" : "hover:bg-stone-50/70"}`}
                    >
                      <td className="px-5 py-3">
                        <div className="flex items-center gap-2.5">
                          {selectedId === p.id && (
                            <div className="w-0.5 h-8 bg-amber-500 rounded-full -ml-2.5 mr-2" />
                          )}
                          <Avatar initials={p.initials} />
                          <span className="font-medium text-stone-800">
                            {p.name}
                          </span>
                        </div>
                      </td>
                      <td className="px-3 py-3 text-stone-400 font-mono text-xs">
                        {p.phone}
                      </td>
                      <td className="px-3 py-3">
                        <span
                          className={`px-2 py-0.5 rounded-full text-xs font-medium ${p.role === "moderador" ? "bg-purple-100 text-purple-700" : "bg-stone-100 text-stone-500"}`}
                        >
                          {p.role}
                        </span>
                      </td>
                      <td className="px-3 py-3 text-right font-mono text-stone-700">
                        {p.wildcards}
                      </td>
                      <td className="px-3 py-3 text-right font-mono font-semibold text-stone-800">
                        {p.totalPoints.toLocaleString("es-MX")}
                      </td>
                      <td className="px-3 py-3 text-right">
                        <StreakBadge days={p.streak} atRisk={atRisk} />
                      </td>
                      <td className="px-5 py-3 text-right text-xs text-stone-400 font-mono">
                        {p.maxStreak}d
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Drawer */}
        {selected && (
          <div className="w-72 bg-white rounded-xl border border-stone-200 shadow-sm flex flex-col flex-shrink-0 overflow-hidden">
            <div className="px-5 py-4 border-b border-stone-100 flex items-start justify-between">
              <div className="flex items-center gap-2.5">
                <Avatar initials={selected.initials} size="md" />
                <div>
                  <p className="font-semibold text-stone-800 text-sm leading-tight">
                    {selected.name}
                  </p>
                  <p className="text-[11px] text-stone-400 font-mono mt-0.5">
                    {selected.phone}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setSelectedId(null)}
                className="text-stone-400 hover:text-stone-600 transition-colors mt-0.5"
              >
                <IconX />
              </button>
            </div>
            <div className="p-4 space-y-4 overflow-auto flex-1">
              <div className="grid grid-cols-2 gap-2">
                {[
                  {
                    label: "Puntos totales",
                    value: selected.totalPoints.toLocaleString("es-MX"),
                    accent: false,
                  },
                  {
                    label: "Racha actual",
                    value: `${selected.streak}d 🔥`,
                    accent: true,
                  },
                  { label: "Racha máxima", value: `${selected.maxStreak}d`, accent: false },
                  {
                    label: "Comodines",
                    value: String(selected.wildcards),
                    accent: false,
                  },
                ].map((stat) => (
                  <div key={stat.label} className="bg-stone-50 rounded-lg p-3">
                    <p className="text-[10px] text-stone-400 uppercase tracking-wide">
                      {stat.label}
                    </p>
                    <p
                      className={`text-base font-bold font-mono mt-0.5 ${stat.accent ? "text-amber-600" : "text-stone-800"}`}
                    >
                      {stat.value}
                    </p>
                  </div>
                ))}
              </div>

              <div>
                <p className="text-[10px] font-semibold text-stone-400 uppercase tracking-wider mb-2">
                  Participaciones recientes
                </p>
                {PARTICIPATIONS.filter(
                  (p) => p.participantId === selected.id
                ).length > 0 ? (
                  <div className="space-y-1.5">
                    {PARTICIPATIONS.filter(
                      (p) => p.participantId === selected.id
                    ).map((p) => (
                      <div
                        key={p.id}
                        className="flex items-center justify-between py-1.5 border-b border-stone-50 gap-2"
                      >
                        <CategoryBadge category={p.category} />
                        <span className="text-[10px] text-stone-400 font-mono">
                          {p.time}
                        </span>
                        <StatusBadge status={p.status} />
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-stone-400 py-3 text-center">
                    Sin participaciones registradas hoy
                  </p>
                )}
              </div>

              <div className="space-y-2 pt-1">
                <button className="w-full py-2 text-sm font-medium bg-amber-50 text-amber-700 rounded-lg border border-amber-200 hover:bg-amber-100 transition-colors">
                  Editar racha manualmente
                </button>
                <button className="w-full py-2 text-sm font-medium bg-stone-50 text-stone-700 rounded-lg border border-stone-200 hover:bg-stone-100 transition-colors">
                  Agregar puntos manualmente
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
