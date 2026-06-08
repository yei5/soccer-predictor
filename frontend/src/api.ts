import axios from 'axios';
import type { League, Team } from './types';

export const API_BASE = 'http://localhost:8000';

interface RawLeague {
  id: number;
  name: string;
  code: string;
  emblem?: string;
  area?: { name?: string };
  plan?: string;
}

interface RawTeam {
  id: number;
  name: string;
  shortName?: string;
  tla?: string;
  crest?: string;
}

export function normalizeLeagues(data: unknown): League[] {
  if (!Array.isArray(data)) return [];
  return (data as RawLeague[])
    .filter((league) => league?.id && league?.code && league?.name)
    .map((league) => ({
      id: league.id,
      name: league.name,
      code: league.code,
      emblem: league.emblem ?? '',
      areaName: league.area?.name ?? '',
      plan: league.plan ?? '',
    }))
    .sort((a, b) => a.name.localeCompare(b.name));
}

export function normalizeTeams(data: unknown): Team[] {
  const raw = Array.isArray(data)
    ? data
    : (data as { teams?: RawTeam[] })?.teams;

  if (!Array.isArray(raw)) return [];

  return raw
    .filter((team) => team?.id && team?.name)
    .map((team) => ({
      id: team.id,
      name: team.name,
      shortName: team.shortName ?? team.name,
      tla: team.tla ?? '---',
      crest: team.crest ?? '',
    }))
    .sort((a, b) => a.name.localeCompare(b.name));
}

export async function fetchLeaguesFromApi(): Promise<League[]> {
  const res = await axios.get(`${API_BASE}/leagues`);
  return normalizeLeagues(res.data);
}

export async function fetchTeamsFromApi(competitionCode: string): Promise<Team[]> {
  const res = await axios.get(`${API_BASE}/teams/${competitionCode}`);
  return normalizeTeams(res.data);
}
