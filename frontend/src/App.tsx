import React, { useEffect, useMemo, useState } from 'react'
import { Play, RefreshCw, CheckCircle2, AlertCircle, Loader2, Download } from 'lucide-react'

const backend = '/api'

type Step = {
  status: string
  summary?: string | null
  error?: string | null
  started_at?: string | null
  finished_at?: string | null
  data?: any
}

type RunRecord = {
  id: string
  steps: Record<string, Step>
  created_at: string
  updated_at: string
}

const stepOrder = ['analyst', 'manual', 'autotests', 'standards', 'optimize']

const statusBadge = (status: string) => {
  const map: Record<string, string> = {
    queued: 'bg-slate-800 text-slate-200',
    running: 'bg-amber-500/20 text-amber-200',
    success: 'bg-emerald-500/20 text-emerald-200',
    failed: 'bg-rose-500/20 text-rose-200'
  }
  return map[status] || 'bg-slate-800 text-slate-200'
}

function App() {
  const [requirements, setRequirements] = useState('')
  const [openapi, setOpenapi] = useState('')
  const [model, setModel] = useState('')
  const [models, setModels] = useState<string[]>([])
  const [runs, setRuns] = useState<string[]>([])
  const [currentRun, setCurrentRun] = useState<RunRecord | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetch(`${backend}/models`)
      .then((r) => r.json())
      .then((data) => {
        const ids = (data?.data || []).map((m: any) => m.id)
        setModels(ids)
        if (ids.length > 0) setModel(ids[0])
      })
      .catch(() => setError('Failed to load models'))

    fetch(`${backend}/runs`)
      .then((r) => r.json())
      .then((data) => setRuns(data.runs || []))
      .catch(() => {})
  }, [])

  const fetchRun = async (id: string) => {
    const resp = await fetch(`${backend}/runs/${id}`)
    const data = await resp.json()
    const runRaw = data.files?.['run.json']
    if (runRaw) {
      const parsed = JSON.parse(runRaw) as RunRecord
      setCurrentRun(parsed)
    }
  }

  useEffect(() => {
    if (!currentRun) return
    const done = stepOrder.every((s) => currentRun.steps?.[s]?.status === 'success' || currentRun.steps?.[s]?.status === 'failed')
    if (done) return
    const id = setInterval(() => fetchRun(currentRun.id), 1500)
    return () => clearInterval(id)
  }, [currentRun])

  const runPipeline = async () => {
    setError('')
    setLoading(true)
    try {
      const resp = await fetch(`${backend}/runs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ requirements, openapi, model })
      })
      const data = await resp.json()
      if (!resp.ok) throw new Error(data.detail || 'Run failed to start')
      const runId = data.run_id
      await fetchRun(runId)
      setRuns((r) => Array.from(new Set([runId, ...r])))
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const statusIcon = (status: string) => {
    if (status === 'running') return <Loader2 className="h-4 w-4 animate-spin" />
    if (status === 'success') return <CheckCircle2 className="h-4 w-4 text-emerald-400" />
    if (status === 'failed') return <AlertCircle className="h-4 w-4 text-rose-400" />
    return <RefreshCw className="h-4 w-4 text-slate-300" />
  }

  const downloadLink = useMemo(() => (currentRun ? `${backend}/runs/${currentRun.id}/download` : ''), [currentRun])

  return (
    <div className="min-h-screen grid grid-cols-[260px_1fr]">
      <aside className="border-r border-slate-800 bg-slate-900/60 p-4 flex flex-col gap-4">
        <div>
          <h1 className="text-xl font-semibold">TestOps Copilot</h1>
          <p className="text-sm text-slate-400">Agentic pipeline powered by Cloud.ru</p>
        </div>
        <button className="button-primary flex items-center gap-2" onClick={runPipeline} disabled={loading}>
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
          Run pipeline
        </button>
        <div className="space-y-2">
          <div className="text-xs uppercase text-slate-400">Settings</div>
          <select className="w-full bg-slate-800 text-slate-100 rounded-md p-2" value={model} onChange={(e) => setModel(e.target.value)}>
            {models.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </div>
        <div className="space-y-2 flex-1 overflow-y-auto">
          <div className="text-xs uppercase text-slate-400">Runs</div>
          <div className="space-y-2">
            {runs.map((r) => (
              <button key={r} className="w-full text-left bg-slate-800 hover:bg-slate-700 p-2 rounded" onClick={() => fetchRun(typeof r === 'string' ? r : JSON.parse(r).id)}>
                {typeof r === 'string' ? r : JSON.parse(r).id}
              </button>
            ))}
          </div>
        </div>
        {downloadLink && (
          <a href={downloadLink} className="flex items-center gap-2 text-sm text-slate-200 hover:text-white">
            <Download className="h-4 w-4" /> Download artifacts
          </a>
        )}
      </aside>
      <main className="p-6 space-y-4">
        {error && <div className="card border-rose-500/40 text-rose-200">{error}</div>}
        <div className="grid grid-cols-2 gap-4">
          <div className="card space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="font-semibold">Input</h2>
              <span className="badge">UI Requirements / OpenAPI</span>
            </div>
            <textarea
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 h-40"
              placeholder="Paste UI requirements"
              value={requirements}
              onChange={(e) => setRequirements(e.target.value)}
            />
            <textarea
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 h-40"
              placeholder="Paste OpenAPI (yaml/json)"
              value={openapi}
              onChange={(e) => setOpenapi(e.target.value)}
            />
          </div>
          <div className="space-y-3">
            {stepOrder.map((step) => {
              const data = currentRun?.steps?.[step]
              return (
                <div key={step} className="card">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      {statusIcon(data?.status || 'queued')}
                      <span className="capitalize">{step}</span>
                    </div>
                    <span className={`badge ${statusBadge(data?.status || 'queued')}`}>{data?.status || 'queued'}</span>
                  </div>
                  <div className="text-sm text-slate-400">
                    {data?.summary || data?.error || 'Waiting...'}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
