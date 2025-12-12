import React, { useEffect, useState } from 'react'

const backend = '/api'

type Tab = 'manual-ui' | 'manual-api' | 'autotests-ui' | 'autotests-api' | 'validate' | 'history'

type RunInfo = { id: string, files: Record<string, string> }

function App() {
  const [tab, setTab] = useState<Tab>('manual-ui')
  const [requirements, setRequirements] = useState('')
  const [openapi, setOpenapi] = useState('')
  const [output, setOutput] = useState('')
  const [loading, setLoading] = useState(false)
  const [runs, setRuns] = useState<RunInfo[]>([])
  const [selectedRun, setSelectedRun] = useState<RunInfo | null>(null)
  const [lastRunId, setLastRunId] = useState<string>('')

  const loadHistory = async () => {
    const resp = await fetch(`${backend}/runs`)
    const data = await resp.json()
    setRuns(data.runs || [])
  }

  useEffect(() => {
    if (tab === 'history') {
      void loadHistory()
    }
  }, [tab])

  const run = async () => {
    setLoading(true)
    let endpoint = ''
    let body: any = {}
    if (tab === 'manual-ui') {
      endpoint = '/generate/manual/ui'
      body.requirements = requirements
    } else if (tab === 'manual-api') {
      endpoint = '/generate/manual/api'
      body.openapi = openapi
    } else if (tab === 'autotests-ui') {
      endpoint = '/generate/autotests/ui'
      body.requirements = requirements
    } else if (tab === 'autotests-api') {
      endpoint = '/generate/autotests/api'
      body.openapi = openapi
    } else if (tab === 'validate') {
      endpoint = '/validate'
      body.code = output
    } else {
      await loadHistory()
      setLoading(false)
      return
    }
    const resp = await fetch(`${backend}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    const data = await resp.json()
    setOutput(data.code || data.markdown || JSON.stringify(data, null, 2))
    if (data.run_id) {
      setLastRunId(data.run_id)
      await loadHistory()
    }
    setLoading(false)
  }

  const openRun = async (id: string) => {
    const resp = await fetch(`${backend}/runs/${id}`)
    const data = await resp.json()
    setSelectedRun({ id: data.run_id, files: data.files })
  }

  return (
    <div className="app">
      <h1>TestOps Copilot</h1>
      <div className="tabs">
        {['manual-ui','manual-api','autotests-ui','autotests-api','validate','history'].map(t => (
          <button key={t} className={tab===t as Tab ? 'active': ''} onClick={() => setTab(t as Tab)}>{t}</button>
        ))}
      </div>
      {(tab === 'manual-ui' || tab === 'autotests-ui') && (
        <textarea value={requirements} onChange={e => setRequirements(e.target.value)} placeholder="Paste UI requirements" />
      )}
      {(tab === 'manual-api' || tab === 'autotests-api') && (
        <textarea value={openapi} onChange={e => setOpenapi(e.target.value)} placeholder="Paste OpenAPI" />
      )}
      {tab === 'validate' && (
        <textarea value={output} onChange={e => setOutput(e.target.value)} placeholder="Paste code to validate" />
      )}
      <div className="actions">
        <button onClick={run} disabled={loading}>{loading ? 'Running...' : 'Run'}</button>
        {lastRunId && <span className="hint">Last run: {lastRunId}</span>}
      </div>

      {tab !== 'history' && (
        <>
          <h2>Output</h2>
          <pre className="output">{output}</pre>
        </>
      )}

      {tab === 'history' && (
        <div className="history">
          <div className="history-list">
            <div className="history-header">
              <h3>Runs</h3>
              <button onClick={loadHistory} disabled={loading}>Refresh</button>
            </div>
            <ul>
              {runs.map(run => (
                <li key={run.id}>
                  <button onClick={() => openRun(run.id)}>{run.id}</button>
                  <a href={`${backend}/runs/${run.id}/download`} target="_blank" rel="noreferrer">Download zip</a>
                </li>
              ))}
            </ul>
          </div>
          {selectedRun && (
            <div className="run-details">
              <h3>Run {selectedRun.id}</h3>
              {Object.entries(selectedRun.files).map(([name, content]) => (
                <details key={name}>
                  <summary>{name}</summary>
                  <pre className="output">{content}</pre>
                </details>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default App
