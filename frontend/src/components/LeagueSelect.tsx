import { Loader2 } from 'lucide-react';
import type { Lang, League } from '../types';
import { translations } from '../i18n';

interface LeagueSelectProps {
  lang: Lang;
  leagues: League[];
  value: string;
  loading: boolean;
  onChange: (code: string) => void;
}

export function LeagueSelect({ lang, leagues, value, loading, onChange }: LeagueSelectProps) {
  const t = (key: string) => translations[lang][key] ?? key;
  const selected = leagues.find((l) => l.code === value);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">
          {t('league')}
        </label>
        {!loading && leagues.length > 0 && (
          <span className="text-[10px] text-slate-600">
            {t('leaguesCount').replace('{n}', String(leagues.length))}
          </span>
        )}
      </div>

      {loading ? (
        <div className="flex items-center gap-2 p-3 rounded-xl bg-slate-800 border border-slate-700 text-sm text-slate-400">
          <Loader2 className="w-4 h-4 animate-spin" />
          {t('loadingLeagues')}
        </div>
      ) : (
        <select
          className="w-full bg-slate-800 border border-slate-600 rounded-xl p-3 text-sm text-white outline-none focus:ring-2 focus:ring-emerald-500"
          value={value}
          onChange={(e) => onChange(e.target.value)}
        >
          <option value="">{t('selectLeague')}</option>
          {leagues.map((league) => (
            <option key={league.id} value={league.code}>
              {formatLeagueOption(league)}
            </option>
          ))}
        </select>
      )}

      {selected && (
        <div className="flex items-center gap-3 p-3 rounded-xl bg-slate-800/80 border border-emerald-500/20">
          {selected.emblem ? (
            <img
              src={selected.emblem}
              alt=""
              className="w-10 h-10 object-contain"
              onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
            />
          ) : null}
          <div className="min-w-0">
            <p className="font-semibold text-white text-sm truncate">{selected.name}</p>
            <p className="text-xs text-slate-400">
              {selected.code}
              {selected.areaName ? ` · ${selected.areaName}` : ''}
              {selected.plan ? ` · ${selected.plan}` : ''}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

function formatLeagueOption(league: League): string {
  const parts = [league.name, `(${league.code})`];
  if (league.areaName) parts.push(`— ${league.areaName}`);
  return parts.join(' ');
}
