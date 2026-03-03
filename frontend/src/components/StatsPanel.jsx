export default function StatsPanel({ stats, violations, fitness }) {
  if (!stats) return null;

  const hard = violations.filter(v => v.constraint_type === 'hard');
  const soft = violations.filter(v => v.constraint_type === 'soft');
  const isGA = stats.algorithm === 'genetic';

  return (
    <div className="mb-8 space-y-3">
      <div className="flex items-center gap-2 text-xs">
        <span className={`font-medium px-2 py-0.5 rounded ${isGA ? 'bg-violet-100 text-violet-700' : 'bg-indigo-100 text-indigo-700'}`}>
          {isGA ? 'genetic algorithm' : 'backtracking + mrv'}
        </span>
        {fitness && (
          <span className={`font-mono px-2 py-0.5 rounded ${fitness.total >= 0 ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'}`}>
            fitness {fitness.total}
          </span>
        )}
      </div>

      <div className="grid grid-cols-4 gap-3">
        {[
          { value: stats.total_lectures, label: 'scheduled' },
          { value: `${stats.time_seconds.toFixed(3)}s`, label: 'solve time' },
          { value: stats.nodes_explored, label: isGA ? 'evaluated' : 'explored' },
          { value: isGA ? stats.generations_run : stats.backtracks, label: isGA ? 'generations' : 'backtracks' },
        ].map(({ value, label }) => (
          <div key={label} className="bg-white border border-slate-200 rounded-md px-3 py-2.5">
            <div className="text-lg font-semibold text-slate-800 tabular-nums">{value}</div>
            <div className="text-[11px] text-slate-400">{label}</div>
          </div>
        ))}
      </div>

      {fitness && (
        <div className="flex gap-4 text-xs text-slate-500 px-1">
          <span>hard <strong className={fitness.hard_penalty < 0 ? 'text-red-600' : 'text-emerald-600'}>{fitness.hard_penalty}</strong></span>
          <span>soft <strong className={fitness.soft_penalty < 0 ? 'text-amber-600' : 'text-emerald-600'}>{fitness.soft_penalty}</strong></span>
          <span>bonus <strong className="text-emerald-600">+{fitness.bonus}</strong></span>
          {fitness.student_gaps > 0 && <span>gaps <strong className="text-amber-600">{fitness.student_gaps}</strong></span>}
          {isGA && stats.best_generation != null && <span className="text-slate-400">best at gen {stats.best_generation}</span>}
        </div>
      )}

      {hard.length > 0 && (
        <div className="px-3 py-2 bg-red-50 border border-red-200 rounded-md text-xs text-red-700">
          <strong>{hard.length} hard violations:</strong>
          {hard.map((v, i) => <span key={i} className="block ml-2">{v.description}</span>)}
        </div>
      )}

      {soft.length > 0 && (
        <div className="px-3 py-2 bg-amber-50 border border-amber-200 rounded-md text-xs text-amber-700">
          <strong>{soft.length} soft warnings:</strong>
          {soft.map((v, i) => <span key={i} className="block ml-2">{v.description}</span>)}
        </div>
      )}

      {hard.length === 0 && soft.length === 0 && (
        <div className="px-3 py-2 bg-emerald-50 border border-emerald-200 rounded-md text-xs text-emerald-700 font-medium text-center">
          Clean timetable &mdash; no violations
        </div>
      )}
    </div>
  );
}
