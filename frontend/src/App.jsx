import { useState } from 'react';
import InputForm from './components/InputForm';
import TimetableGrid from './components/TimetableGrid';
import TeacherView from './components/TeacherView';
import StatsPanel from './components/StatsPanel';
import { generateTimetable, exportExcel } from './api';
import { SAMPLE_DATA, EXAM_SAMPLE_DATA } from './sampleData';

const INITIAL = { ...SAMPLE_DATA, algorithm: 'backtracking', mode: 'timetable', ga_population: 100, ga_generations: 500, sa_initial_temp: 1000, sa_cooling_rate: 0.995 };

export default function App() {
  const [inputData, setInputData] = useState(INITIAL);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [view, setView] = useState('grid');
  const [showInput, setShowInput] = useState(true);

  async function handleGenerate() {
    setLoading(true);
    setError(null);
    try {
      const res = await generateTimetable(inputData);
      if (res.success) {
        setResult(res);
        setShowInput(false);
      } else {
        setError(res.error || 'Failed to generate timetable');
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleExport() {
    try { await exportExcel(inputData); }
    catch (e) { setError('Export failed: ' + e.message); }
  }

  function handleReset() {
    setResult(null);
    setShowInput(true);
    setError(null);
  }

  function handleModeSwitch(mode) {
    if (mode === 'exam') {
      setInputData({ ...EXAM_SAMPLE_DATA, algorithm: inputData.algorithm, mode: 'exam', ga_population: inputData.ga_population, ga_generations: inputData.ga_generations, sa_initial_temp: inputData.sa_initial_temp, sa_cooling_rate: inputData.sa_cooling_rate });
    } else {
      setInputData({ ...SAMPLE_DATA, algorithm: inputData.algorithm, mode: 'timetable', ga_population: inputData.ga_population, ga_generations: inputData.ga_generations, sa_initial_temp: inputData.sa_initial_temp, sa_cooling_rate: inputData.sa_cooling_rate });
    }
  }

  const algoLabels = { backtracking: 'Backtracking + MRV', genetic: 'Genetic Algorithm', simulated_annealing: 'Simulated Annealing' };
  const algoLabel = algoLabels[inputData.algorithm] || inputData.algorithm;
  const isExam = inputData.mode === 'exam';

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 font-[system-ui]">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded bg-indigo-600 flex items-center justify-center text-white font-bold text-sm">{isExam ? 'E' : 'T'}</div>
            <div>
              <h1 className="text-base font-semibold leading-tight">{isExam ? 'Exam Scheduler' : 'Timetable Scheduler'}</h1>
              <p className="text-xs text-slate-400">graph coloring &middot; constraint satisfaction</p>
            </div>
          </div>
          {result && (
            <div className="flex items-center gap-2">
              <button onClick={() => setView(v => v === 'grid' ? 'teacher' : 'grid')}
                className="px-3 py-1.5 text-xs font-medium border border-slate-200 rounded-md hover:bg-slate-50 transition-colors">
                {view === 'grid' ? 'Teacher view' : 'Grid view'}
              </button>
              <button onClick={handleExport}
                className="px-3 py-1.5 text-xs font-medium bg-emerald-600 text-white rounded-md hover:bg-emerald-700 transition-colors">
                Export .xlsx
              </button>
              <button onClick={handleReset}
                className="px-3 py-1.5 text-xs font-medium border border-slate-200 rounded-md hover:bg-slate-50 transition-colors">
                Edit
              </button>
            </div>
          )}
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">
        {error && (
          <div className="mb-6 px-4 py-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-md">
            {error}
          </div>
        )}

        {showInput && (
          <>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-sm font-medium text-slate-500 uppercase tracking-wide">Configuration</h2>
              <button onClick={() => setInputData(INITIAL)}
                className="text-xs text-indigo-600 hover:text-indigo-800 font-medium">
                Reset to sample data
              </button>
            </div>

            {/* mode toggle */}
            <div className="mb-4 p-4 bg-white border border-slate-200 rounded-lg">
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-3">Scheduling mode</p>
              <div className="flex gap-3">
                {[
                  { value: 'timetable', label: 'Timetable', desc: 'Regular class scheduling with lectures, labs, and teacher assignments.' },
                  { value: 'exam', label: 'Exam', desc: 'Exam scheduling: max 1 exam/day per group, spread across days.' },
                ].map(opt => (
                  <label key={opt.value}
                    className={`flex-1 p-3 rounded-md border cursor-pointer transition-all text-sm ${inputData.mode === opt.value ? 'border-indigo-400 bg-indigo-50' : 'border-slate-200 hover:border-slate-300'}`}>
                    <input type="radio" name="mode" value={opt.value} checked={inputData.mode === opt.value}
                      onChange={() => handleModeSwitch(opt.value)} className="sr-only" />
                    <span className="font-medium block">{opt.label}</span>
                    <span className="text-xs text-slate-500 mt-0.5 block">{opt.desc}</span>
                  </label>
                ))}
              </div>
            </div>

            <InputForm data={inputData} onChange={setInputData} isExam={isExam} />

            {/* algorithm picker */}
            <div className="mt-6 p-5 bg-white border border-slate-200 rounded-lg">
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-3">Solving algorithm</p>
              <div className="flex gap-3">
                {[
                  { value: 'backtracking', label: 'Backtracking + MRV', desc: 'Exact solver. Guarantees valid output. Fast for small inputs.' },
                  { value: 'genetic', label: 'Genetic Algorithm', desc: 'Heuristic optimizer. Better soft constraint handling. Slower.' },
                  { value: 'simulated_annealing', label: 'Simulated Annealing', desc: 'Iterative optimizer. Good balance of speed and quality.' },
                ].map(opt => (
                  <label key={opt.value}
                    className={`flex-1 p-3 rounded-md border cursor-pointer transition-all text-sm ${inputData.algorithm === opt.value ? 'border-indigo-400 bg-indigo-50' : 'border-slate-200 hover:border-slate-300'}`}>
                    <input type="radio" name="algo" value={opt.value} checked={inputData.algorithm === opt.value}
                      onChange={() => setInputData({ ...inputData, algorithm: opt.value })} className="sr-only" />
                    <span className="font-medium block">{opt.label}</span>
                    <span className="text-xs text-slate-500 mt-0.5 block">{opt.desc}</span>
                  </label>
                ))}
              </div>
              {inputData.algorithm === 'genetic' && (
                <div className="flex gap-4 mt-3 ml-1">
                  <label className="text-xs text-slate-500">
                    Population
                    <input type="number" value={inputData.ga_population}
                      onChange={e => setInputData({ ...inputData, ga_population: +e.target.value || 100 })}
                      className="ml-2 w-16 border border-slate-200 rounded px-1.5 py-0.5 text-xs" />
                  </label>
                  <label className="text-xs text-slate-500">
                    Generations
                    <input type="number" value={inputData.ga_generations}
                      onChange={e => setInputData({ ...inputData, ga_generations: +e.target.value || 500 })}
                      className="ml-2 w-16 border border-slate-200 rounded px-1.5 py-0.5 text-xs" />
                  </label>
                </div>
              )}
              {inputData.algorithm === 'simulated_annealing' && (
                <div className="flex gap-4 mt-3 ml-1">
                  <label className="text-xs text-slate-500">
                    Initial temp
                    <input type="number" value={inputData.sa_initial_temp}
                      onChange={e => setInputData({ ...inputData, sa_initial_temp: +e.target.value || 1000 })}
                      className="ml-2 w-20 border border-slate-200 rounded px-1.5 py-0.5 text-xs" />
                  </label>
                  <label className="text-xs text-slate-500">
                    Cooling rate
                    <input type="number" step="0.001" value={inputData.sa_cooling_rate}
                      onChange={e => setInputData({ ...inputData, sa_cooling_rate: +e.target.value || 0.995 })}
                      className="ml-2 w-20 border border-slate-200 rounded px-1.5 py-0.5 text-xs" />
                  </label>
                </div>
              )}
            </div>

            <div className="mt-8 text-center">
              <button onClick={handleGenerate} disabled={loading}
                className="px-6 py-2.5 bg-indigo-600 text-white text-sm font-medium rounded-md hover:bg-indigo-700 disabled:opacity-50 transition-colors">
                {loading ? 'Solving...' : `Generate (${algoLabel})`}
              </button>
            </div>
          </>
        )}

        {result && (
          <>
            <StatsPanel stats={result.stats} violations={result.violations} fitness={result.fitness} />
            {view === 'grid' ? (
              <TimetableGrid
                schedule={result.schedule}
                groups={inputData.student_groups}
                days={inputData.working_days}
                periodsPerDay={inputData.periods_per_day}
                lunchAfter={inputData.constraints.lunch_break_after_period}
              />
            ) : (
              <TeacherView schedule={result.schedule} teachers={inputData.teachers} days={inputData.working_days} />
            )}
          </>
        )}
      </main>
    </div>
  );
}
