export default function TeacherView({ schedule, teachers, days }) {
  return (
    <div className="space-y-3">
      {teachers.map(teacher => {
        const classes = schedule
          .filter(s => s.teacher_id === teacher.id)
          .sort((a, b) => days.indexOf(a.day) - days.indexOf(b.day) || a.period - b.period);

        if (!classes.length) return null;

        return (
          <div key={teacher.id} className="bg-white border border-slate-200 rounded-lg p-4">
            <div className="flex items-baseline gap-2 mb-3">
              <span className="text-sm font-semibold text-slate-700">{teacher.name}</span>
              <span className="text-xs text-slate-400">{classes.length} classes/wk</span>
            </div>
            <div className="grid grid-cols-5 gap-1.5">
              {days.map(day => {
                const dayClasses = classes.filter(s => s.day === day);
                return (
                  <div key={day}>
                    <div className="text-[10px] font-medium text-slate-400 uppercase tracking-wide mb-1">{day.slice(0, 3)}</div>
                    {dayClasses.length === 0 ? (
                      <div className="text-[10px] text-slate-300 italic">free</div>
                    ) : dayClasses.map((c, i) => (
                      <div key={i} className="text-[11px] bg-slate-50 border border-slate-100 rounded px-1.5 py-1 mb-1">
                        <span className="font-mono text-slate-500">P{c.period}</span>{' '}
                        <span className="font-medium text-slate-700">{c.subject_code}</span>{' '}
                        <span className="text-slate-400">{c.group_name}</span>
                      </div>
                    ))}
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}
