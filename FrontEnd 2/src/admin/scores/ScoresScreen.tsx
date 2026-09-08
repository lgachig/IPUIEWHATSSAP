import { useState } from "react";
import type { Category } from "../../types";
import { PARTICIPANTS, CATEGORY_LABELS } from "../../data/mockData";
import { StatusBadge, CategoryBadge } from "../../components/common/Primitives";

export function ScoresScreen() {
  const [userVal, setUserVal] = useState("");
  const [cat, setCat] = useState<Category>("lectura");
  const [pts, setPts] = useState(10);
  const [reason, setReason] = useState("");
  const [isValid, setIsValid] = useState(true);
  const [date, setDate] = useState("2026-09-08");

  const selectedUser = PARTICIPANTS.find((p) => String(p.id) === userVal);
  const canPreview = !!selectedUser && reason.trim().length > 0;

  const recent = [
    {
      user: "Carlos Mendoza",
      admin: "Gabriela Mora",
      cat: "detective_biblico" as Category,
      pts: 20,
      reason: "Corrección bot — respuesta no detectada",
      date: "08 sep 08:47",
      valid: true,
    },
    {
      user: "Diego Hernández",
      admin: "Gabriela Mora",
      cat: "lectura" as Category,
      pts: -10,
      reason: "Respuesta duplicada eliminada",
      date: "07 sep 16:22",
      valid: false,
    },
    {
      user: "Patricia Reyes",
      admin: "Gabriela Mora",
      cat: "bono_semanal" as Category,
      pts: 50,
      reason: "Bono semanal no aplicado automáticamente",
      date: "01 sep 09:00",
      valid: true,
    },
  ];

  return (
    <div className="p-7 space-y-6 max-w-3xl">
      <div>
        <h1 className="text-[1.65rem] font-bold text-stone-900 font-display">
          Ajuste Manual de Puntos
        </h1>
        <p className="text-sm text-stone-400 mt-0.5">
          Para cuando el sistema automático no validó correctamente una
          participación
        </p>
      </div>

      <div className="bg-white rounded-xl border border-stone-200 shadow-sm p-6 space-y-5">
        <div className="grid grid-cols-2 gap-4">
          <div className="col-span-2">
            <label className="block text-xs font-semibold text-stone-600 mb-1.5 uppercase tracking-wide">
              Participante
            </label>
            <select
              value={userVal}
              onChange={(e) => setUserVal(e.target.value)}
              className="w-full border border-stone-200 rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-amber-400"
            >
              <option value="">Seleccionar participante…</option>
              {PARTICIPANTS.map((p) => (
                <option key={p.id} value={String(p.id)}>
                  {p.name} — {p.phone}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-stone-600 mb-1.5 uppercase tracking-wide">
              Fecha
            </label>
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="w-full border border-stone-200 rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-amber-400"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-stone-600 mb-1.5 uppercase tracking-wide">
              Categoría
            </label>
            <select
              value={cat}
              onChange={(e) => setCat(e.target.value as Category)}
              className="w-full border border-stone-200 rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-amber-400"
            >
              {(Object.keys(CATEGORY_LABELS) as Category[]).map((k) => (
                <option key={k} value={k}>
                  {CATEGORY_LABELS[k]}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-stone-600 mb-1.5 uppercase tracking-wide">
              Puntos a agregar
            </label>
            <input
              type="number"
              value={pts}
              onChange={(e) => setPts(Number(e.target.value))}
              className="w-full border border-stone-200 rounded-lg px-3 py-2 text-sm bg-white font-mono focus:outline-none focus:ring-2 focus:ring-amber-400"
            />
            <p className="text-[11px] text-stone-400 mt-1">
              Valores negativos corrigen errores previos
            </p>
          </div>

          <div className="flex items-end pb-4">
            <label className="flex items-center gap-2.5 cursor-pointer">
              <input
                type="checkbox"
                checked={isValid}
                onChange={(e) => setIsValid(e.target.checked)}
                className="w-4 h-4 rounded accent-amber-500"
              />
              <span className="text-sm text-stone-700">
                Marcar como válido
              </span>
            </label>
          </div>

          <div className="col-span-2">
            <label className="block text-xs font-semibold text-stone-600 mb-1.5 uppercase tracking-wide">
              Motivo del ajuste{" "}
              <span className="text-red-400 normal-case font-normal">
                (obligatorio)
              </span>
            </label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              rows={3}
              placeholder="Describe brevemente por qué se hace este ajuste manual…"
              className="w-full border border-stone-200 rounded-lg px-3 py-2 text-sm bg-white resize-none focus:outline-none focus:ring-2 focus:ring-amber-400"
            />
          </div>
        </div>

        {/* Preview */}
        {canPreview && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 space-y-3">
            <p className="text-[11px] font-semibold text-amber-700 uppercase tracking-wider">
              Vista previa del registro
            </p>
            <div className="grid grid-cols-3 gap-x-4 gap-y-2 text-sm">
              <div>
                <span className="text-stone-400 text-xs">Usuario</span>
                <p className="font-medium text-stone-800">
                  {selectedUser.name}
                </p>
              </div>
              <div>
                <span className="text-stone-400 text-xs">Fecha</span>
                <p className="font-mono text-stone-800">{date}</p>
              </div>
              <div>
                <span className="text-stone-400 text-xs">Categoría</span>
                <p className="mt-0.5">
                  <CategoryBadge category={cat} />
                </p>
              </div>
              <div>
                <span className="text-stone-400 text-xs">Puntos</span>
                <p
                  className={`font-mono font-bold text-base ${pts >= 0 ? "text-emerald-700" : "text-red-600"}`}
                >
                  {pts >= 0 ? `+${pts}` : pts}
                </p>
              </div>
              <div>
                <span className="text-stone-400 text-xs">Estado</span>
                <p className="mt-0.5">
                  <StatusBadge status={isValid ? "valido" : "invalido"} />
                </p>
              </div>
              <div className="col-span-3">
                <span className="text-stone-400 text-xs">Motivo</span>
                <p className="text-stone-700 text-sm">{reason}</p>
              </div>
            </div>
          </div>
        )}

        <div className="flex items-center gap-3">
          <button className="px-5 py-2 bg-amber-500 text-white rounded-lg text-sm font-semibold hover:bg-amber-600 transition-colors">
            Guardar ajuste
          </button>
          <button className="px-5 py-2 bg-stone-100 text-stone-600 rounded-lg text-sm font-medium hover:bg-stone-200 transition-colors">
            Cancelar
          </button>
        </div>
      </div>

      {/* Audit table */}
      <div className="bg-white rounded-xl border border-stone-200 shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-stone-100">
          <h2 className="text-sm font-semibold text-stone-900">
            Ajustes manuales recientes
          </h2>
          <p className="text-xs text-stone-400 mt-0.5">
            Auditoría — quién cambió qué y cuándo
          </p>
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-stone-50 border-b border-stone-100">
              {["Participante", "Admin", "Categoría", "Pts", "Motivo", "Fecha"].map((h, i) => (
                <th
                  key={h}
                  className={`py-2.5 text-[11px] font-semibold text-stone-400 uppercase tracking-wider ${i === 0 ? "text-left px-5" : i === 5 ? "text-right px-5" : i >= 3 ? "text-right px-3" : "text-left px-3"}`}
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-stone-50">
            {recent.map((r, i) => (
              <tr key={i} className="hover:bg-stone-50/70 transition-colors">
                <td className="px-5 py-3 font-medium text-stone-800">
                  {r.user}
                </td>
                <td className="px-3 py-3 text-xs text-stone-500">{r.admin}</td>
                <td className="px-3 py-3">
                  <CategoryBadge category={r.cat} />
                </td>
                <td className="px-3 py-3 text-right font-mono font-semibold">
                  <span className={r.pts >= 0 ? "text-emerald-700" : "text-red-600"}>
                    {r.pts >= 0 ? `+${r.pts}` : r.pts}
                  </span>
                </td>
                <td className="px-3 py-3 text-xs text-stone-500 max-w-[200px] truncate">
                  {r.reason}
                </td>
                <td className="px-5 py-3 text-right text-xs text-stone-400 font-mono">
                  {r.date}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
