const SUBJECT_COLORS = [
  ['bg-indigo-50', 'text-indigo-700', 'border-indigo-200'],
  ['bg-emerald-50', 'text-emerald-700', 'border-emerald-200'],
  ['bg-amber-50', 'text-amber-700', 'border-amber-200'],
  ['bg-rose-50', 'text-rose-700', 'border-rose-200'],
  ['bg-violet-50', 'text-violet-700', 'border-violet-200'],
  ['bg-cyan-50', 'text-cyan-700', 'border-cyan-200'],
  ['bg-orange-50', 'text-orange-700', 'border-orange-200'],
  ['bg-fuchsia-50', 'text-fuchsia-700', 'border-fuchsia-200'],
];

export default function TimetableGrid({ schedule, groups, days, periodsPerDay, lunchAfter }) {
  const colorMap = {};
  let idx = 0;
  schedule.forEach(s => {
    if (!colorMap[s.subject_code]) {
      colorMap[s.subject_code] = SUBJECT_COLORS[idx % SUBJECT_COLORS.length];
      idx++;
    }
  });

  function find(groupId, day, period) {
    return schedule.find(s => s.group_id === groupId && s.day === day && s.period === period);
  }

  return (
    <div className="space-y-8">
      {groups.map(group => (
        <div key={group.id}>
          <h3 className="text-sm font-semibold text-slate-700 mb-2">
            {group.name} <span className="text-slate-400 font-normal">({group.strength} students)</span>
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-xs border-collapse">
              <thead>
                <tr>
                  <th className="bg-slate-700 text-white px-2 py-2 text-left font-medium w-14">Period</th>
                  {days.map(d => (
                    <th key={d} className="bg-slate-700 text-white px-3 py-2 text-center font-medium">{d}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {Array.from({ length: periodsPerDay }, (_, i) => i + 1).map(period => (
                  <>
                    <tr key={period} className="group">
                      <td className="bg-slate-50 text-center text-slate-500 font-mono px-2 py-2.5 border-b border-slate-100">
                        {period}
                      </td>
                      {days.map(day => {
                        const cls = find(group.id, day, period);
                        if (!cls) {
                          return <td key={day} className="text-center px-2 py-2.5 border-b border-slate-100 text-slate-300">&mdash;</td>;
                        }
                        const [bg, text, border] = colorMap[cls.subject_code] || SUBJECT_COLORS[0];
                        return (
                          <td key={day} className={`text-center px-2 py-2 border-b border-slate-100 ${bg} ${text}`}>
                            <div className="font-semibold leading-tight">
                              {cls.subject_code}
                              {cls.is_lab && <span className="ml-1 text-[10px] bg-amber-200 text-amber-800 px-1 rounded font-medium">LAB</span>}
                            </div>
                            <div className="text-[10px] opacity-60 leading-tight mt-0.5">{cls.teacher_name}</div>
                            <div className="text-[10px] opacity-50 leading-tight">{cls.room_name}</div>
                          </td>
                        );
                      })}
                    </tr>
                    {period === lunchAfter && (
                      <tr key={`lunch-${period}`}>
                        <td colSpan={1 + days.length} className="text-center py-1 bg-amber-50/60 text-amber-500 text-[10px] tracking-widest uppercase border-b border-amber-100">
                          lunch break
                        </td>
                      </tr>
                    )}
                  </>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  );
}
