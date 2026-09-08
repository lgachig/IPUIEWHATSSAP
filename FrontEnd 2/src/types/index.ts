export type Screen =
  | "dashboard"
  | "participants"
  | "scores"
  | "streaks"
  | "activities"
  | "logs";

export type Status = "valido" | "invalido" | "pendiente";
export type LogLevel = "info" | "warning" | "error";

export type Category =
  | "lectura"
  | "pregunta"
  | "detective_biblico"
  | "reto_20_segundos"
  | "completa_idea"
  | "reto_sorpresa"
  | "prueba_fuego"
  | "bono_semanal"
  | "bono_mensual";

export interface Participant {
  id: number;
  name: string;
  initials: string;
  phone: string;
  registered: string;
  role: "participante" | "moderador";
  wildcards: number;
  totalPoints: number;
  streak: number;
  maxStreak: number;
  answeredToday: boolean;
}

export interface Participation {
  id: number;
  participantId: number;
  name: string;
  initials: string;
  phone: string;
  category: Category;
  points: number;
  time: string;
  status: Status;
}

export interface LogEntry {
  id: number;
  type: string;
  description: string;
  user: string;
  level: LogLevel;
  timestamp: string;
}
