import { useState } from 'react'
import { analyzeText } from '../api/analyze'

const RESULT_FIELDS = [
  { key: 'words_count', label: 'Words' },
  { key: 'sentences_count', label: 'Sentences' },
  { key: 'characters_count', label: 'Characters' },
  { key: 'total_syllables', label: 'Syllables' },
  { key: 'avg_syllables_per_word', label: 'Avg. syllables / word' },
  { key: 'avg_words_per_sentence', label: 'Avg. words / sentence' },
  { key: 'avg_characters_per_word', label: 'Avg. characters / word' },
]

function formatValue(value) {
  return typeof value === 'number' && !Number.isInteger(value)
    ? value.toFixed(2)
    : String(value)
}

function AnalyzePage() {
  const [text, setText] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    const trimmed = text.trim()

    if (!trimmed) {
      setError('Please paste some Kyrgyz text to analyze.')
      setResult(null)
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const data = await analyzeText(trimmed)
      setResult(data)
    } catch (err) {
      setError(err.message || 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="bg-paper-soft py-12">
      <div className="max-w-4xl mx-auto px-8">
        <p className="text-text-highlight font-body font-semibold text-sm uppercase tracking-wide mb-3">
          Текстти анализдөө
        </p>
        <h1 className="font-display text-4xl font-bold text-ink mb-3">
          Analyze Kyrgyz text
        </h1>
        <p className="font-body text-ink/70 mb-8 max-w-2xl">
          Paste a passage and we will measure word, sentence, and syllable
          patterns, then return ARI and Kyrgyz readability scores from the API.
        </p>

        <form
          onSubmit={handleSubmit}
          className="bg-paper rounded-2xl shadow-sm border border-paper p-6 md:p-8"
        >
          <label htmlFor="analyze-text" className="font-body text-sm font-medium text-ink mb-2 block">
            Kyrgyz text
          </label>
          <textarea
            id="analyze-text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={10}
            placeholder="Текстти бул жерге жазыңыз..."
            className="w-full font-body text-ink bg-paper-soft rounded-xl px-4 py-3 border border-transparent focus:outline-none focus:ring-2 focus:ring-primary resize-y min-h-40"
          />

          {error && (
            <p className="mt-3 font-body text-sm text-red-700" role="alert">
              {error}
            </p>
          )}

          <div className="mt-6 flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className="bg-primary hover:bg-primary-dark disabled:opacity-60 text-white font-body font-medium px-6 py-3 rounded-full transition-colors"
            >
              {loading ? 'Analyzing…' : 'Analyze text'}
            </button>
          </div>
        </form>

        {result && (
          <div className="mt-8 space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="bg-paper rounded-2xl p-6 border border-paper shadow-sm">
                <p className="font-body text-sm text-ink/60 mb-1">Kyrgyz readability</p>
                <p className="font-display text-4xl font-bold text-primary">
                  {formatValue(result.readability_score)}
                </p>
                <p className="font-body text-sm text-ink/60 mt-2">
                  Higher scores usually mean easier text.
                </p>
              </div>
              <div className="bg-paper rounded-2xl p-6 border border-paper shadow-sm">
                <p className="font-body text-sm text-ink/60 mb-1">ARI score</p>
                <p className="font-display text-4xl font-bold text-text-highlight">
                  {formatValue(result.ari_score)}
                </p>
                <p className="font-body text-sm text-ink/60 mt-2">
                  Approximate U.S. grade level.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {RESULT_FIELDS.map(({ key, label }) => (
                <div
                  key={key}
                  className="bg-paper rounded-2xl p-4 border border-paper shadow-sm"
                >
                  <p className="font-body text-xs text-ink/60 mb-1">{label}</p>
                  <p className="font-display text-2xl font-semibold text-ink">
                    {formatValue(result[key])}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  )
}

export default AnalyzePage
