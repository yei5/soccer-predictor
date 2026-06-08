import { Trophy, Activity, Loader2, Sparkles, ChevronRight } from 'lucide-react';
import type { Lang, League, Message, Team } from '../types';
import { translations } from '../i18n';
import { LeagueSelect } from './LeagueSelect';
import { TeamPicker } from './TeamPicker';
import { PredictionCard } from './PredictionCard';

interface PredictPanelProps {
  lang: Lang;
  leagues: League[];
  leaguesLoading: boolean;
  teams: Team[];
  teamsLoading: boolean;
  selectedLeague: string;
  team1: number | null;
  team2: number | null;
  loading: boolean;
  messages: Message[];
  onLeagueChange: (code: string) => void;
  onTeam1Change: (id: number | null) => void;
  onTeam2Change: (id: number | null) => void;
  onSwapTeams: () => void;
  onPredict: () => void;
}

export function PredictPanel({
  lang,
  leagues,
  leaguesLoading,
  teams,
  teamsLoading,
  selectedLeague,
  team1,
  team2,
  loading,
  messages,
  onLeagueChange,
  onTeam1Change,
  onTeam2Change,
  onSwapTeams,
  onPredict,
}: PredictPanelProps) {
  const t = (key: string) => translations[lang][key] ?? key;
  const step = !selectedLeague ? 1 : !team1 || !team2 ? 2 : 3;
  const canAnalyze = Boolean(selectedLeague && team1 && team2 && team1 !== team2 && !loading);
  const selectedLeagueObj = leagues.find((l) => l.code === selectedLeague);
  const homeTeam = teams.find((x) => x.id === team1);
  const awayTeam = teams.find((x) => x.id === team2);
  const latestPrediction = [...messages].reverse().find((m) => m.prediction_data);

  return (
    <div className="flex flex-col lg:flex-row h-full min-h-0">
      {/* Controls — only visible in Predict tab */}
      <div className="lg:w-[380px] shrink-0 border-b lg:border-b-0 lg:border-r border-slate-800 bg-[#131c2e] overflow-y-auto">
        <div className="p-5 border-b border-slate-700/60">
          <h2 className="text-lg font-bold text-white">{t('predictTab')}</h2>
          <p className="text-xs text-slate-500 mt-1">{t('predictTabDesc')}</p>
        </div>

        <div className="px-5 py-3 flex items-center gap-1 text-[10px] font-bold uppercase tracking-wide">
          {[
            { n: 1, label: t('stepLeague') },
            { n: 2, label: t('stepTeams') },
            { n: 3, label: t('stepAnalyze') },
          ].map((s, i) => (
            <div key={s.n} className="flex items-center gap-1">
              <div
                className={`flex items-center gap-1.5 px-2 py-1 rounded-lg ${
                  step >= s.n ? 'text-emerald-400 bg-emerald-500/10' : 'text-slate-600'
                }`}
              >
                <span
                  className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] ${
                    step >= s.n ? 'bg-emerald-500 text-white' : 'bg-slate-700 text-slate-500'
                  }`}
                >
                  {s.n}
                </span>
                <span>{s.label}</span>
              </div>
              {i < 2 && <ChevronRight className="w-3 h-3 text-slate-600" />}
            </div>
          ))}
        </div>

        <div className="p-5 space-y-5">
          <LeagueSelect
            lang={lang}
            leagues={leagues}
            value={selectedLeague}
            loading={leaguesLoading}
            onChange={onLeagueChange}
          />

          {!selectedLeague ? (
            <div className="rounded-xl border border-dashed border-slate-700 p-5 text-center text-sm text-slate-500">
              {t('noLeague')}
            </div>
          ) : teamsLoading ? (
            <div className="flex items-center justify-center gap-2 p-6 rounded-xl border border-slate-700 text-sm text-slate-400">
              <Loader2 className="w-4 h-4 animate-spin" />
              {t('loadingTeams')}
            </div>
          ) : teams.length === 0 ? (
            <div className="rounded-xl border border-dashed border-slate-700 p-5 text-center text-sm text-slate-500">
              {t('noTeams')}
            </div>
          ) : (
            <>
              <p className="text-[10px] text-slate-600 text-right -mt-2">
                {t('teamsCount').replace('{n}', String(teams.length))}
              </p>
              <TeamPicker
                lang={lang}
                teams={teams}
                team1={team1}
                team2={team2}
                disabled={loading}
                onTeam1Change={onTeam1Change}
                onTeam2Change={onTeam2Change}
                onSwap={onSwapTeams}
              />
            </>
          )}

          <div className="rounded-xl bg-slate-800/50 border border-slate-700/60 p-4 text-sm">
            {canAnalyze ? (
              <p className="text-emerald-400 font-medium flex items-center gap-2">
                <Sparkles className="w-4 h-4" /> {t('readyToAnalyze')}
              </p>
            ) : (
              <p className="text-slate-500">{t('pickTeamsHint')}</p>
            )}
            {selectedLeagueObj && homeTeam && awayTeam && (
              <p className="text-xs text-slate-400 mt-2">
                {selectedLeagueObj.name} · {homeTeam.shortName} vs {awayTeam.shortName}
              </p>
            )}
          </div>

          <button
            onClick={onPredict}
            disabled={!canAnalyze}
            className="w-full bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-700 disabled:text-slate-500 disabled:cursor-not-allowed text-white font-bold py-3.5 rounded-xl shadow-lg shadow-emerald-900/40 transition-all flex items-center justify-center gap-2"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Trophy className="w-5 h-5" />}
            {loading ? t('runningAnalysis') : t('analyzeMatch')}
          </button>

          <p className="flex items-center gap-2 text-[11px] text-slate-500">
            <Activity className="w-3.5 h-3.5 shrink-0" />
            {t('tripleSource')}
          </p>
        </div>
      </div>

      {/* Results */}
      <div className="flex-1 overflow-y-auto p-6 md:p-8 bg-[#0b1220]">
        <div className="max-w-2xl mx-auto space-y-6">
          {!latestPrediction && !loading && (
            <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-8 text-center">
              <Trophy className="w-12 h-12 text-emerald-500 mx-auto mb-4 opacity-80" />
              <p className="text-slate-400 text-sm leading-relaxed">{t('welcome')}</p>
            </div>
          )}
          {loading && (
            <div className="flex items-center justify-center gap-3 p-8 rounded-2xl border border-slate-800 bg-slate-900/40">
              <Loader2 className="w-6 h-6 animate-spin text-emerald-500" />
              <span className="text-slate-400">{t('runningAnalysis')}</span>
            </div>
          )}
          {latestPrediction?.prediction_data && !loading && (
            <PredictionCard data={latestPrediction.prediction_data} lang={lang} />
          )}
        </div>
      </div>
    </div>
  );
}
