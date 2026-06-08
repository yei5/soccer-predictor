import { Trophy, TrendingUp, Target } from 'lucide-react';
import type { Lang, PredictionData } from '../types';
import { translations } from '../i18n';
import { ProbabilityBar } from './ProbabilityBar';

interface PredictionCardProps {
  data: PredictionData;
  lang: Lang;
}

const confidenceColors: Record<string, string> = {
  low: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
  medium: 'bg-sky-500/20 text-sky-300 border-sky-500/30',
  high: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
};

export function PredictionCard({ data, lang }: PredictionCardProps) {
  const t = (key: string) => translations[lang][key] ?? key;
  const confLabel =
    data.confidence_label ||
    translations[lang][data.confidence] ||
    data.confidence;
  const outcomeLabel = data.outcome_label || data.outcome;
  const probs = [
    { key: 'home', label: t('homeWin'), value: data.home_win_probability, color: 'bg-emerald-500', active: data.outcome === 'home_win' },
    { key: 'draw', label: t('draw'), value: data.draw_probability, color: 'bg-slate-400', active: data.outcome === 'draw' },
    { key: 'away', label: t('awayWin'), value: data.away_win_probability, color: 'bg-violet-500', active: data.outcome === 'away_win' },
  ];
  const [homeScore, awayScore] = data.predicted_score.split('-');

  return (
    <div className="rounded-2xl border border-slate-700/80 bg-gradient-to-br from-[#1e293b] to-[#0f172a] overflow-hidden shadow-xl">
      <div className="px-5 py-4 border-b border-slate-700/60 bg-slate-800/40 flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-emerald-400">
          <Trophy className="w-4 h-4" />
          <span className="text-xs font-bold uppercase tracking-wider">{t('analysisInsight')}</span>
        </div>
        <span className={`text-xs px-2.5 py-1 rounded-full border ${confidenceColors[data.confidence] || confidenceColors.medium}`}>
          {t('confidence')}: {confLabel}
        </span>
      </div>

      {(data.home_team || data.away_team) && (
        <div className="px-5 py-6 flex items-center justify-center gap-4">
          <div className="text-center flex-1">
            <p className="text-xs text-slate-500 uppercase mb-1">{t('homeTeam')}</p>
            <p className="font-bold text-white text-sm md:text-base">{data.home_team}</p>
          </div>
          <div className="flex flex-col items-center px-4 py-3 rounded-xl bg-slate-800/80 border border-slate-700">
            <span className="text-2xl font-black text-white tracking-widest">
              {homeScore}<span className="text-slate-500 mx-1">-</span>{awayScore}
            </span>
            <span className="text-[10px] text-slate-500 mt-1 uppercase">{t('predictedScore')}</span>
          </div>
          <div className="text-center flex-1">
            <p className="text-xs text-slate-500 uppercase mb-1">{t('awayTeam')}</p>
            <p className="font-bold text-white text-sm md:text-base">{data.away_team}</p>
          </div>
        </div>
      )}

      <div className="px-5 pb-4">
        <div className="flex items-center gap-2 mb-3">
          <Target className="w-4 h-4 text-emerald-400" />
          <span className="text-sm font-semibold text-slate-200">{outcomeLabel}</span>
        </div>
      </div>

      <div className="px-5 pb-5 space-y-3">
        <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{t('probabilities')}</p>
        {probs.map((p) => (
          <ProbabilityBar
            key={p.key}
            label={p.label}
            value={p.value}
            color={p.color}
            highlight={p.active}
          />
        ))}
      </div>

      {data.key_factors?.length > 0 && (
        <div className="px-5 pb-5 border-t border-slate-700/50 pt-4">
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp className="w-4 h-4 text-sky-400" />
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{t('keyFactors')}</p>
          </div>
          <ul className="space-y-2">
            {data.key_factors.map((factor, i) => (
              <li key={i} className="flex gap-2 text-sm text-slate-300">
                <span className="text-emerald-500 font-bold">•</span>
                <span>{factor}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {data.rationale && (
        <div className="px-5 pb-5 border-t border-slate-700/50 pt-4">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">{t('analysis')}</p>
          <p className="text-sm text-slate-300 leading-relaxed">{data.rationale}</p>
        </div>
      )}

      {data.ml_probabilities && (
        <div className="px-5 py-3 bg-slate-900/50 border-t border-slate-700/50 text-xs text-slate-500">
          {t('mlModel')}: {Math.round(data.ml_probabilities.home_win * 100)}% / {Math.round(data.ml_probabilities.draw * 100)}% / {Math.round(data.ml_probabilities.away_win * 100)}%
        </div>
      )}
    </div>
  );
}
