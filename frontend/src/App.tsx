import React, { useState } from 'react'

const backend = '/api'

type Tab = 'manual-ui' | 'manual-api' | 'autotests-ui' | 'autotests-api' | 'validate'

function App() {
  const [tab, setTab] = useState<Tab>('manual-ui')
  const [requirements, setRequirements] = useState('')
  const [openapi, setOpenapi] = useState('')
  const [output, setOutput] = useState('')
  const [loading, setLoading] = useState(false)

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
    } else {
      endpoint = '/validate'
      body.code = output
    }
    const resp = await fetch(`${backend}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    const data = await resp.json()
    setOutput(data.code || data.markdown || JSON.stringify(data, null, 2))
    setLoading(false)
  }

  return (
    <div className="app">
      <h1>TestOps Copilot</h1>
      <div className="tabs">
        {['manual-ui','manual-api','autotests-ui','autotests-api','validate'].map(t => (
          <button key={t} className={tab===t as Tab ? 'active': ''} onClick={() => setTab(t as Tab)}>{t}</button>
        ))}
      </div>
      {(tab === 'manual-ui' || tab === 'autotests-ui') && (
        <textarea value={requirements} onChange={e => setRequirements(e.target.value)} placeholder="Paste UI requirements" />
      )}
      {(tab === 'manual-api' || tab === 'autotests-api') && (
        <textarea value={openapi} onChange={e => setOpenapi(e.target.value)} placeholder="Paste OpenAPI" />
      )}
      <button onClick={run} disabled={loading}>{loading ? 'Running...' : 'Run'}</button>
      <h2>Output</h2>
      <pre className="output">{output}</pre>
    </div>
  )
}

export default App
