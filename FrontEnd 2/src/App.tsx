import { useState } from "react";
import type { Screen } from "./types";
import { Sidebar } from "./components/layout/Sidebar";
import { DashboardScreen } from "./admin/dashboard/DashboardScreen";
import { ParticipantsScreen } from "./admin/participants/ParticipantsScreen";
import { ScoresScreen } from "./admin/scores/ScoresScreen";
import { StreaksScreen } from "./admin/streaks/StreaksScreen";
import { ActivitiesScreen } from "./admin/activities/ActivitiesScreen";
import { LogsScreen } from "./admin/logs/LogsScreen";

export default function App() {
  const [screen, setScreen] = useState<Screen>("dashboard");
  const [dark, setDark] = useState(false);

  return (
    <div className={`flex h-full font-sans ${dark ? "dark" : ""}`}>
      <Sidebar
        screen={screen}
        setScreen={setScreen}
        dark={dark}
        setDark={setDark}
      />
      <main className="flex-1 overflow-auto bg-stone-50">
        {screen === "dashboard" && <DashboardScreen />}
        {screen === "participants" && <ParticipantsScreen />}
        {screen === "scores" && <ScoresScreen />}
        {screen === "streaks" && <StreaksScreen />}
        {screen === "activities" && <ActivitiesScreen />}
        {screen === "logs" && <LogsScreen />}
      </main>
    </div>
  );
}
