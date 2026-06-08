export type Lang = 'en' | 'es';

export interface League {
  id: number;
  name: string;
  code: string;
  emblem: string;
  areaName?: string;
  plan?: string;
}

export interface Team {
  id: number;
  name: string;
  shortName: string;
  tla: string;
  crest: string;
}

export interface Session {
  id: number;
  title: string;
  created_at: string;
}

export interface PredictionData {
  outcome: string;
  outcome_label?: string;
  home_win_probability: number;
  draw_probability: number;
  away_win_probability: number;
  predicted_score: string;
  confidence: string;
  confidence_label?: string;
  key_factors: string[];
  rationale: string;
  home_team?: string;
  away_team?: string;
  ml_probabilities?: Record<string, number>;
  language?: string;
}

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  prediction_data?: PredictionData;
}
