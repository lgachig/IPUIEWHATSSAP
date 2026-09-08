import { useState } from "react";
import type { Category } from "../../types";
import { CATEGORY_LABELS } from "../../data/mockData";

export function ActivitiesScreen() {
  const [selectedDay, setSelectedDay] = useState<number | null>(8);
  const daysWithActivities = [1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 15, 16, 17, 18, 19, 22, 23, 24];
  const today = 8;
  const firstDayOfWeek = new Date(2026, 8, 1).getDay();
  const daysInMonth = 30;
  const weekdays = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"];

  return (
    <div className="p-7 space-y-5">
      <div>
        <h1 className="text-[1.65rem] font-bold text-stone-900 font-display">
          Actividades Diarias
        </h1>
        <p className="text-sm text-stone-400 mt-0.5">
          Septiembre 2026 — lecturas y retos del mes
        </p>
      </div>

      <div className="grid grid-cols-5 gap-5">
        {/* Calendar */}
        <div className="col-span-3 bg-white rounded-xl border border-stone-200 shadow-sm p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-stone-800">
              Septiembre 2026
            </h2>
            <div className="flex items-center gap-4 text-xs text-stone-400">
              <span className="flex items-center gap-1">
                <span className="text-emerald-500">✓</span> Cargada
              </span>
              <span className="flex items-center gap-1">
                <span className="text-orange-400">⚠</span> Sin actividad
              </span>
            </div>
          </div>

          <div className="grid grid-cols-7 gap-1 mb-1">
            {weekdays.map((d) => (
              <div
                key={d}
                className="text-center text-[11px] font-semibold text-stone-400 py-1.5"
              >
                {d}
              </div>
            ))}
          </div>
          <div className="grid grid-cols-7 gap-1">
            {Array.from({ length: firstDayOfWeek }).map((_, i) => (
              <div key={`e${i}`} />
            ))}
            {Array.from({ length: daysInMonth }).map((_, i) => {
              const day = i + 1;
              const has = daysWithActivities.includes(day);
              const isToday = day === today;
              const isFuture = day > today;
              const isSelected = selectedDay === day;

              return (
                <button
                  key={day}
                  onClick={() =>
                    setSelectedDay(isSelected ? null : day)
                  }
                  className={`aspect-square flex flex-col items-center justify-center rounded-lg text-sm font-medium transition-all
                    ${isToday ? "bg-amber-500 text-white shadow-md shadow-amber-200" : ""}
                    ${!isToday && isSelected ? "bg-amber-50 border-2 border-amber-400 text-amber-800" : ""}
                    ${!isToday && !isSelected && !isFuture ? "hover:bg-stone-50 text-stone-700" : ""}
                    ${isFuture && !isSelected ? "text-stone-300 hover:bg-stone-50" : ""}
                  `}
                >
                  <span className="leading-none">{day}</span>
                  {!isFuture && (
                    <span
                      className={`text-[9px] mt-0.5 leading-none ${isToday ? "text-amber-100" : has ? "text-emerald-500" : "text-orange-400"}`}
                    >
                      {has ? "✓" : "⚠"}
                    </span>
                  )}
                </button>
              );
            })}
          </div>

          <div className="mt-4 pt-3 border-t border-stone-100 flex items-center gap-4 text-xs text-stone-400">
            <span>
              {daysWithActivities.filter((d) => d <= today).length} días cargados
            </span>
            <span>·</span>
            <span>
              {today - daysWithActivities.filter((d) => d <= today).length} días sin actividad
            </span>
          </div>
        </div>

        {/* Day form */}
        <div className="col-span-2 bg-white rounded-xl border border-stone-200 shadow-sm p-5">
          {selectedDay ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-stone-900">
                  {selectedDay} de septiembre, 2026
                </h3>
                {daysWithActivities.includes(selectedDay) && (
                  <span className="text-xs bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full font-medium">
                    Cargada
                  </span>
                )}
              </div>

              {[
                {
                  label: "Lectura del día",
                  placeholder: "Ej: Salmos 23:1-6",
                  defaultVal: daysWithActivities.includes(selectedDay)
                    ? "Filipenses 4:4-9"
                    : "",
                },
                {
                  label: "Tema",
                  placeholder: "Ej: La paz de Dios",
                  defaultVal: daysWithActivities.includes(selectedDay)
                    ? "El gozo y la paz en Cristo"
                    : "",
                },
              ].map((f) => (
                <div key={f.label}>
                  <label className="block text-[11px] font-semibold text-stone-500 uppercase tracking-wide mb-1">
                    {f.label}
                  </label>
                  <input
                    type="text"
                    placeholder={f.placeholder}
                    defaultValue={f.defaultVal}
                    className="w-full border border-stone-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400"
                  />
                </div>
              ))}

              <div>
                <label className="block text-[11px] font-semibold text-stone-500 uppercase tracking-wide mb-1">
                  Tipo de actividad
                </label>
                <select className="w-full border border-stone-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400">
                  {(Object.keys(CATEGORY_LABELS) as Category[]).slice(0, 6).map((k) => (
                    <option key={k} value={k}>
                      {CATEGORY_LABELS[k]}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-stone-500 uppercase tracking-wide mb-1">
                  Pregunta / Reto
                </label>
                <textarea
                  rows={2}
                  placeholder="Escribe la pregunta o reto del día…"
                  defaultValue={
                    daysWithActivities.includes(selectedDay)
                      ? "¿Cuál es la exhortación principal de Pablo en Filipenses 4:4?"
                      : ""
                  }
                  className="w-full border border-stone-200 rounded-lg px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-amber-400"
                />
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-stone-500 uppercase tracking-wide mb-1">
                  Respuesta esperada
                </label>
                <input
                  type="text"
                  placeholder="Respuesta clave"
                  defaultValue={
                    daysWithActivities.includes(selectedDay)
                      ? "Regocijaos en el Señor"
                      : ""
                  }
                  className="w-full border border-stone-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400"
                />
              </div>

              <button className="w-full py-2 bg-amber-500 text-white rounded-lg text-sm font-semibold hover:bg-amber-600 transition-colors">
                {daysWithActivities.includes(selectedDay)
                  ? "Actualizar actividad"
                  : "Crear actividad"}
              </button>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full py-16 text-center">
              <span className="text-5xl mb-4">📖</span>
              <p className="text-sm font-semibold text-stone-700">
                Selecciona un día
              </p>
              <p className="text-xs text-stone-400 mt-1.5 leading-relaxed">
                Haz clic en cualquier día del calendario para crear o editar su
                actividad
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
