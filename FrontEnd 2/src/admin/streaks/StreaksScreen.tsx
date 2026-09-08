import { useState } from "react";
import { PARTICIPANTS } from "../../data/mockData";
import { Avatar, StreakBadge } from "../../components/common/Primitives";

export function StreaksScreen() {
  const [confirmReset, setConfirmReset] = useState<number | null>(null);
  const sorted = [...PARTICIPANTS].sort((a, b) => b.streak - a.streak);

  return (
    <div className="p-7 space-y-5">
      <div>
        <h1 className="text-[1.65rem] font-bold text-stone-900 font-display">
          Gestión de Rachas
        </h1>
        <p className="text-sm text-stone-400 mt-0.5">
          Repara o resetea rachas manualmente
        </p>
      </div>

      <div className="bg-white rounded-xl border border-stone-200 shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-stone-50 border-b border-stone-100">
              <th className="text-left px-5 py-3 text-[11px] font-semibold text-stone-400 uppercase tracking-wider">Participante</th>
              <th className="text-right px-3 py-3 text-[11px] font-semibold text-stone-400 uppercase tracking-wider">Racha actual</th>
              <th className="text-right px-3 py-3 text-[11px] font-semibold text-stone-400 uppercase tracking-wider">Racha máx.</th>
              <th className="text-right px-3 py-3 text-[11px] font-semibold text-stone-400 uppercase tracking-wider">Comodines mes</th>
              <th className="text-center px-3 py-3 text-[11px] font-semibold text-stone-400 uppercase tracking-wider">Respondió hoy</th>
              <th className="text-right px-5 py-3 text-[11px] font-semibold text-stone-400 uppercase tracking-wider">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-stone-50">
            {sorted.map((p) => {
              const atRisk = !p.answeredToday && p.streak > 4;
              return (
                <tr
                  key={p.id}
                  className={`transition-colors ${atRisk ? "bg-orange-50/50" : "hover:bg-stone-50/70"}`}
                >
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-2.5">
                      <Avatar initials={p.initials} />
                      <span className="font-medium text-stone-800">
                        {p.name}
                      </span>
                    </div>
                  </td>
                  <td className="px-3 py-3 text-right">
                    <StreakBadge days={p.streak} atRisk={atRisk} />
                  </td>
                  <td className="px-3 py-3 text-right text-xs text-stone-400 font-mono">
                    {p.maxStreak}d
                  </td>
                  <td className="px-3 py-3 text-right">
                    <span
                      className={`font-mono font-semibold ${p.wildcards === 0 ? "text-red-400" : "text-stone-700"}`}
                    >
                      {p.wildcards}
                    </span>
                  </td>
                  <td className="px-3 py-3 text-center">
                    {p.answeredToday ? (
                      <span className="text-emerald-500 font-bold">✓</span>
                    ) : (
                      <span className="text-red-400">✗</span>
                    )}
                  </td>
                  <td className="px-5 py-3">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        disabled={p.wildcards === 0}
                        className={`px-3 py-1.5 text-xs font-medium rounded-lg border transition-colors ${p.wildcards > 0 ? "bg-amber-50 text-amber-700 border-amber-200 hover:bg-amber-100" : "bg-stone-50 text-stone-300 border-stone-200 cursor-not-allowed"}`}
                        title={
                          p.wildcards === 0
                            ? "Sin comodines disponibles"
                            : "Reparar usando un comodín"
                        }
                      >
                        🃏 Reparar
                      </button>
                      <button
                        onClick={() => setConfirmReset(p.id)}
                        className="px-3 py-1.5 text-xs font-medium rounded-lg border bg-red-50 text-red-600 border-red-200 hover:bg-red-100 transition-colors"
                      >
                        Resetear
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Confirm modal */}
      {confirmReset !== null && (
        <div
          className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 backdrop-blur-sm"
          onClick={() => setConfirmReset(null)}
        >
          <div
            className="bg-white rounded-2xl p-6 max-w-sm w-full mx-4 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <p className="text-lg font-bold text-stone-900 font-display">
              ¿Resetear racha?
            </p>
            <p className="text-sm text-stone-500 mt-2">
              Esto pondrá la racha de{" "}
              <strong>
                {PARTICIPANTS.find((p) => p.id === confirmReset)?.name}
              </strong>{" "}
              a 0. Esta acción se registrará en los logs.
            </p>
            <div className="flex gap-3 mt-5">
              <button
                onClick={() => setConfirmReset(null)}
                className="flex-1 py-2 text-sm font-medium bg-stone-100 text-stone-700 rounded-lg hover:bg-stone-200 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={() => setConfirmReset(null)}
                className="flex-1 py-2 text-sm font-semibold bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
              >
                Sí, resetear
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
