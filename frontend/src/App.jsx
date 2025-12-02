import { useState, useRef, useEffect } from 'react'
import axios from 'axios'

export default function App() {
  const [code, setCode] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  async function analyze() {
    setLoading(true)
    setResult(null)
    try {
      const resp = await axios.post('/api/analyze', { code, apply_fix: false })
      setResult(resp.data)
    } catch (err) {
      setResult({ error: err?.response?.data || err.message })
    } finally {
      setLoading(false)
    }
  }

  const previewRef = useRef(null)
  const textareaRef = useRef(null)

  const escapeHtml = (str) =>
    str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')

  useEffect(() => {
    const pre = previewRef.current
    if (!pre) return
    try {
      const P = window.Prism
      if (P && P.highlightElement) {
        pre.textContent = code || ' '
        P.highlightElement(pre)
      } else {
        pre.innerHTML = escapeHtml(code || ' ')
      }
    } catch (e) {
      pre.innerHTML = escapeHtml(code || ' ')
    }
  }, [code])

  useEffect(() => {
    const ta = textareaRef.current
    const pre = previewRef.current
    if (!ta || !pre) return
    const onScroll = () => {
      pre.scrollTop = ta.scrollTop
      pre.scrollLeft = ta.scrollLeft
    }
    ta.addEventListener('scroll', onScroll)
    return () => ta.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <div className="app">
      <header className="header">
        <h1>BICS Chatbot</h1>
        <p className="subtitle">Analise trechos Python com o corpus local</p>
      </header>

      <main className="container">
        <section className="editor">
          <h2>Editor</h2>
          <div className="code-editor">
            <pre
              ref={previewRef}
              className="language-python preview"
              aria-hidden="true"
            />
            <textarea
              ref={textareaRef}
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder={`Digite ou cole trechos de código Python aqui...`}
              spellCheck={false}
            />
          </div>
          <div className="controls">
            <button onClick={analyze} disabled={loading || !code.trim()}>
              {loading ? 'Analisando…' : 'Analisar código'}
            </button>
            <button
              className="secondary"
              onClick={() => {
                setCode('')
                setResult(null)
              }}
            >
              Limpar
            </button>
          </div>
        </section>

        <section className="result">
          <h2>Resultado</h2>
          <div className="result-body">
            {result ? (
              <pre>{JSON.stringify(result, null, 2)}</pre>
            ) : (
              <div className="empty">Nenhum resultado ainda, analise algum código.</div>
            )}
          </div>
        </section>
      </main>
    </div>
  )
}
