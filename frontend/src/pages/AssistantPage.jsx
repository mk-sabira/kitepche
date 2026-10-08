import { useState } from 'react'
import { askAssistant } from '@/api/assistant'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'

function AssistantPage() {
  const [text, setText] = useState('')
  const [question, setQuestion] = useState('')
  const [language, setLanguage] = useState('en')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    const trimmedText = text.trim()
    const trimmedQuestion = question.trim()

    if (!trimmedText || !trimmedQuestion) {
      setError('Please fill in both the text and the question.')
      setResult(null)
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const data = await askAssistant({
        text: trimmedText,
        question: trimmedQuestion,
        language,
      })
      setResult(data)
    } catch (err) {
      setError(err.message || 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="mx-auto max-w-3xl px-8 py-12">
      <p className="text-highlight font-body font-semibold text-sm uppercase tracking-wide mb-3">
        AI assistant
      </p>
      <h1 className="font-display text-4xl font-bold text-ink mb-8">
        Ask about a Kyrgyz text
      </h1>

      <Card>
        <CardContent className="pt-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <label htmlFor="text" className="font-body font-semibold text-ink">
                Text
              </label>
              <Textarea
                id="text"
                rows={6}
                placeholder="Paste a Kyrgyz text here"
                value={text}
                onChange={(e) => setText(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="question" className="font-body font-semibold text-ink">
                Question
              </label>
              <Input
                id="question"
                placeholder="Is this suitable for a 7-year-old?"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="language" className="font-body font-semibold text-ink">
                Answer language
              </label>
              <Select value={language} onValueChange={setLanguage}>
                <SelectTrigger id="language" className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="en">English</SelectItem>
                  <SelectItem value="ru">Русский</SelectItem>
                  <SelectItem value="ky">Кыргызча</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <Button type="submit" disabled={loading}>
              {loading ? 'Thinking…' : 'Ask'}
            </Button>
          </form>
        </CardContent>
      </Card>

      {result && (
        <Card className="mt-8">
          <CardContent className="space-y-4 pt-6">
            <p className="font-body text-ink whitespace-pre-wrap">{result.answer}</p>
            {result.tools_used.length > 0 && (
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-body text-sm text-ink/60">Tools used:</span>
                {result.tools_used.map((tool) => (
                  <Badge key={tool} variant="secondary">
                    {tool}
                  </Badge>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </main>
  )
}

export default AssistantPage