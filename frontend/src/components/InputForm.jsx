import { useState } from 'react';

function Section({ title, count, defaultOpen = false, children }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="bg-white border border-slate-200 rounded-lg mb-3 overflow-hidden">
      <button type="button" onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-slate-50 transition-colors">
        <span className="text-sm font-medium text-slate-700">{title}</span>
        <div className="flex items-center gap-2">
          {count != null && <span className="text-xs text-slate-400 tabular-nums">{count}</span>}
          <svg className={`w-3.5 h-3.5 text-slate-400 transition-transform ${open ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>
      {open && <div className="px-4 pb-4 border-t border-slate-100">{children}</div>}
    </div>
  );
}

function Field({ label, value, onChange, type = 'text', className = '', ...props }) {
  return (
    <input type={type} placeholder={label} value={value}
      onChange={e => onChange(type === 'number' ? (+e.target.value || 0) : e.target.value)}
      className={`border border-slate-200 rounded px-2 py-1.5 text-xs focus:outline-none focus:border-indigo-400 transition-colors ${className}`}
      {...props} />
  );
}

export default function InputForm({ data, onChange, isExam = false }) {
  function update(key, val) {
    onChange({ ...data, [key]: val });
  }

  function updateItem(section, idx, field, val) {
    const items = [...data[section]];
    items[idx] = { ...items[idx], [field]: val };
    update(section, items);
  }

  function removeItem(section, idx) {
    update(section, data[section].filter((_, i) => i !== idx));
  }

  return (
    <div>
      <Section title={isExam ? "Invigilators" : "Teachers"} count={data.teachers.length} defaultOpen={true}>
        <div className="space-y-2 mt-3">
          {data.teachers.map((t, i) => (
            <div key={i} className="flex flex-col gap-1.5 p-2.5 bg-slate-50 rounded border border-slate-100">
              <div className="flex gap-2">
                <Field label="ID" value={t.id} onChange={v => updateItem('teachers', i, 'id', v)} className="w-14" />
                <Field label="Name" value={t.name} onChange={v => updateItem('teachers', i, 'name', v)} className="flex-1" />
                <button onClick={() => removeItem('teachers', i)} className="text-xs text-red-400 hover:text-red-600 px-1">remove</button>
              </div>
              <Field label="Subjects (comma-separated IDs, e.g. S1, S2)"
                value={Array.isArray(t.subjects) ? t.subjects.join(', ') : t.subjects}
                onChange={v => updateItem('teachers', i, 'subjects', v.split(',').map(s => s.trim()).filter(Boolean))}
                className="w-full" />
            </div>
          ))}
        </div>
        <button onClick={() => update('teachers', [...data.teachers, { id: `T${data.teachers.length + 1}`, name: '', subjects: [] }])}
          className="text-xs text-indigo-600 hover:text-indigo-800 font-medium mt-2 block">+ teacher</button>
      </Section>

      <Section title={isExam ? "Exam halls" : "Rooms"} count={data.rooms.length}>
        <div className="space-y-2 mt-3">
          {data.rooms.map((r, i) => (
            <div key={i} className="flex items-center gap-2 p-2 bg-slate-50 rounded border border-slate-100">
              <Field label="ID" value={r.id} onChange={v => updateItem('rooms', i, 'id', v)} className="w-14" />
              <Field label="Name" value={r.name} onChange={v => updateItem('rooms', i, 'name', v)} className="flex-1" />
              <Field label="Cap" type="number" value={r.capacity} onChange={v => updateItem('rooms', i, 'capacity', v)} className="w-16" />
              <select value={r.type} onChange={e => updateItem('rooms', i, 'type', e.target.value)}
                className="border border-slate-200 rounded px-1.5 py-1.5 text-xs bg-white">
                <option value="lecture_hall">Lecture</option>
                <option value="lab">Lab</option>
              </select>
              <button onClick={() => removeItem('rooms', i)} className="text-xs text-red-400 hover:text-red-600 px-1">remove</button>
            </div>
          ))}
        </div>
        <button onClick={() => update('rooms', [...data.rooms, { id: `R${data.rooms.length + 1}`, name: '', capacity: 60, type: 'lecture_hall' }])}
          className="text-xs text-indigo-600 hover:text-indigo-800 font-medium mt-2 block">+ room</button>
      </Section>

      <Section title={isExam ? "Exams" : "Subjects"} count={data.subjects.length}>
        <div className="space-y-2 mt-3">
          {data.subjects.map((s, i) => (
            <div key={i} className="p-2.5 bg-slate-50 rounded border border-slate-100">
              <div className="flex gap-2 mb-1.5">
                <Field label="ID" value={s.id} onChange={v => updateItem('subjects', i, 'id', v)} className="w-14" />
                <Field label="Name" value={s.name} onChange={v => updateItem('subjects', i, 'name', v)} className="flex-1" />
                <Field label="Code" value={s.code} onChange={v => updateItem('subjects', i, 'code', v)} className="w-16" />
                <button onClick={() => removeItem('subjects', i)} className="text-xs text-red-400 hover:text-red-600 px-1">remove</button>
              </div>
              <div className="flex gap-3 items-center text-xs">
                <label className="text-slate-500">Lectures/wk
                  <Field type="number" value={s.lectures_per_week} onChange={v => updateItem('subjects', i, 'lectures_per_week', v)} className="w-12 ml-1" />
                </label>
                <label className="text-slate-500 flex items-center gap-1">
                  <input type="checkbox" checked={s.requires_lab} onChange={e => updateItem('subjects', i, 'requires_lab', e.target.checked)} />
                  Lab
                </label>
                {s.requires_lab && (
                  <label className="text-slate-500">Lab hrs
                    <Field type="number" value={s.lab_hours} onChange={v => updateItem('subjects', i, 'lab_hours', v)} className="w-12 ml-1" />
                  </label>
                )}
              </div>
            </div>
          ))}
        </div>
        <button onClick={() => update('subjects', [...data.subjects, { id: `S${data.subjects.length + 1}`, name: '', code: '', lectures_per_week: 3, requires_lab: false, lab_hours: 0 }])}
          className="text-xs text-indigo-600 hover:text-indigo-800 font-medium mt-2 block">+ subject</button>
      </Section>

      <Section title={isExam ? "Student groups (examinees)" : "Student groups"} count={data.student_groups.length}>
        <div className="space-y-2 mt-3">
          {data.student_groups.map((g, i) => (
            <div key={i} className="p-2.5 bg-slate-50 rounded border border-slate-100">
              <div className="flex gap-2 mb-1.5">
                <Field label="ID" value={g.id} onChange={v => updateItem('student_groups', i, 'id', v)} className="w-14" />
                <Field label="Name (e.g. CSE-3A)" value={g.name} onChange={v => updateItem('student_groups', i, 'name', v)} className="flex-1" />
                <Field label="Strength" type="number" value={g.strength} onChange={v => updateItem('student_groups', i, 'strength', v)} className="w-16" />
                <button onClick={() => removeItem('student_groups', i)} className="text-xs text-red-400 hover:text-red-600 px-1">remove</button>
              </div>
              <Field label="Subject IDs (comma-separated)"
                value={Array.isArray(g.subjects) ? g.subjects.join(', ') : g.subjects}
                onChange={v => updateItem('student_groups', i, 'subjects', v.split(',').map(s => s.trim()).filter(Boolean))}
                className="w-full" />
            </div>
          ))}
        </div>
        <button onClick={() => update('student_groups', [...data.student_groups, { id: `G${data.student_groups.length + 1}`, name: '', strength: 50, subjects: [] }])}
          className="text-xs text-indigo-600 hover:text-indigo-800 font-medium mt-2 block">+ group</button>
      </Section>

      <Section title="Constraints">
        <div className="grid grid-cols-2 gap-3 mt-3 text-xs">
          <label className="text-slate-500">Periods/day
            <Field type="number" value={data.periods_per_day}
              onChange={v => onChange({ ...data, periods_per_day: v })} className="w-full mt-1" />
          </label>
          <label className="text-slate-500">Lunch after period
            <Field type="number" value={data.constraints.lunch_break_after_period}
              onChange={v => onChange({ ...data, constraints: { ...data.constraints, lunch_break_after_period: v } })} className="w-full mt-1" />
          </label>
          <label className="text-slate-500">Max classes/day (teacher)
            <Field type="number" value={data.constraints.max_classes_per_day_per_teacher}
              onChange={v => onChange({ ...data, constraints: { ...data.constraints, max_classes_per_day_per_teacher: v } })} className="w-full mt-1" />
          </label>
          <label className="text-slate-500">Max classes/day (group)
            <Field type="number" value={data.constraints.max_classes_per_day_per_group}
              onChange={v => onChange({ ...data, constraints: { ...data.constraints, max_classes_per_day_per_group: v } })} className="w-full mt-1" />
          </label>
        </div>
      </Section>
    </div>
  );
}
