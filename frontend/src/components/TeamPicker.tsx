import { ArrowLeftRight } from 'lucide-react';
import type { Lang, Team } from '../types';
import { translations } from '../i18n';

interface TeamPickerProps {
  lang: Lang;
  teams: Team[];
  team1: number | null;
  team2: number | null;
  disabled: boolean;
  onTeam1Change: (id: number | null) => void;
  onTeam2Change: (id: number | null) => void;
  onSwap: () => void;
}

export function TeamPicker({
  lang,
  teams,
  team1,
  team2,
  disabled,
  onTeam1Change,
  onTeam2Change,
  onSwap,
}: TeamPickerProps) {
  const t = (key: string) => translations[lang][key] ?? key;
  const home = teams.find((x) => x.id === team1);
  const away = teams.find((x) => x.id === team2);

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-[1fr_auto_1fr] gap-3 items-end">
        <TeamSlot
          label={t('homeTeam')}
          team={home}
          value={team1}
          teams={teams}
          disabled={disabled}
          excludeId={team2}
          placeholder={t('selectTeam')}
          onChange={onTeam1Change}
          accent="emerald"
        />
        <button
          type="button"
          onClick={onSwap}
          disabled={disabled || !team1 || !team2}
          title={t('swapTeams')}
          className="mb-1 p-2.5 rounded-xl border border-slate-600 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          <ArrowLeftRight className="w-4 h-4 text-slate-300" />
        </button>
        <TeamSlot
          label={t('awayTeam')}
          team={away}
          value={team2}
          teams={teams}
          disabled={disabled}
          excludeId={team1}
          placeholder={t('selectTeam')}
          onChange={onTeam2Change}
          accent="violet"
        />
      </div>
    </div>
  );
}

function TeamSlot({
  label,
  team,
  value,
  teams,
  disabled,
  excludeId,
  placeholder,
  onChange,
  accent,
}: {
  label: string;
  team?: Team;
  value: number | null;
  teams: Team[];
  disabled: boolean;
  excludeId: number | null;
  placeholder: string;
  onChange: (id: number | null) => void;
  accent: 'emerald' | 'violet';
}) {
  const ring = accent === 'emerald' ? 'focus:ring-emerald-500' : 'focus:ring-violet-500';
  const border = accent === 'emerald' ? 'border-emerald-500/30' : 'border-violet-500/30';

  return (
    <div className={`rounded-xl border ${border} bg-slate-800/60 p-3 space-y-2`}>
      <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">{label}</label>
      {team?.crest && (
        <div className="flex justify-center">
          <img src={team.crest} alt="" className="w-12 h-12 object-contain drop-shadow" />
        </div>
      )}
      <select
        className={`w-full bg-slate-900/80 border border-slate-600 rounded-lg p-2.5 text-sm text-white outline-none focus:ring-2 ${ring}`}
        value={value ?? ''}
        onChange={(e) => onChange(e.target.value ? Number(e.target.value) : null)}
        disabled={disabled}
      >
        <option value="">{placeholder}</option>
        {teams
          .filter((t) => t.id !== excludeId)
          .map((t) => (
            <option key={t.id} value={t.id}>
              {t.name} ({t.tla})
            </option>
          ))}
      </select>
      {team && (
        <p className="text-center text-xs text-slate-400 truncate">
          {team.shortName !== team.name ? team.shortName : team.tla}
        </p>
      )}
    </div>
  );
}
