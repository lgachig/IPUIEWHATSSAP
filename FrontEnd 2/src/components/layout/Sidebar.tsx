import type { ReactNode } from "react";
import type { Screen } from "../../types";
import {
  IconHome,
  IconUsers,
  IconStar,
  IconFire,
  IconCalendar,
  IconTerminal,
  IconSun,
  IconMoon,
} from "../icons/Icons";

const NAV: { id: Screen; label: string; icon: ReactNode }[] = [
  { id: "dashboard", label: "Dashboard", icon: <IconHome /> },
  { id: "participants", label: "Participantes", icon: <IconUsers /> },
  { id: "scores", label: "Ajuste de Puntos", icon: <IconStar /> },
  { id: "streaks", label: "Rachas", icon: <IconFire /> },
  { id: "activities", label: "Actividades", icon: <IconCalendar /> },
  { id: "logs", label: "Logs", icon: <IconTerminal /> },
];

export function Sidebar({
  screen,
  setScreen,
  dark,
  setDark,
}: {
  screen: Screen;
  setScreen: (s: Screen) => void;
  dark: boolean;
  setDark: (d: boolean) => void;
}) {
  return (
    <aside className="w-[220px] flex-shrink-0 bg-stone-900 flex flex-col h-full">
      {/* Logo */}
      <div className="px-4 py-5 border-b border-stone-800">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-amber-500 rounded-lg flex items-center justify-center text-white text-sm font-bold flex-shrink-0 font-display">
            MI
          </div>
          <div>
            <p className="text-white text-sm font-semibold leading-tight">
              Modo Íntegro
            </p>
            <p className="text-stone-500 text-[11px]">Panel Admin</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-3 space-y-0.5">
        {NAV.map((item) => (
          <button
            key={item.id}
            onClick={() => setScreen(item.id)}
            className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm transition-all text-left group
              ${screen === item.id
                ? "bg-amber-500 text-white font-semibold shadow-md shadow-amber-900/30"
                : "text-stone-400 hover:text-stone-100 hover:bg-stone-800"
              }`}
          >
            <span
              className={`flex-shrink-0 ${screen === item.id ? "text-white" : "text-stone-500 group-hover:text-stone-300"}`}
            >
              {item.icon}
            </span>
            {item.label}
          </button>
        ))}
      </nav>

      {/* Bottom: theme toggle + user */}
      <div className="px-3 py-4 border-t border-stone-800 space-y-3">
        <button
          onClick={() => setDark(!dark)}
          className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-stone-400 hover:text-stone-200 hover:bg-stone-800 transition-colors text-sm"
        >
          {dark ? <IconSun /> : <IconMoon />}
          {dark ? "Modo claro" : "Modo oscuro"}
        </button>

        <div className="flex items-center gap-2.5 px-3 py-1">
          <div className="w-7 h-7 rounded-full bg-purple-600 flex items-center justify-center text-white text-[11px] font-bold flex-shrink-0">
            GM
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-stone-200 text-xs font-medium truncate">
              Gabriela Mora
            </p>
            <p className="text-stone-500 text-[11px]">Moderadora</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
