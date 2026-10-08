import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'

function AssistantPage() {
  const [text, setText] = useState('')
  const [question, setQuestion] = useState('')

  return (
    <main className="mx-auto max-w-3xl px-8 py-12">
      <p className="text-highlight font-body font-semibold text-sm uppercase tracking-wide mb-3">
        AI assistant
      </p>
      <h1 className="font-display text-4xl font-bold text-ink mb-8">
        Ask about a Kyrgyz text
      </h1>

      <Card>
        <CardContent className="space-y-6 pt-6">
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

          <Button type="button">Ask</Button>
        </CardContent>
      </Card>
    </main>
  )
}

export default AssistantPage