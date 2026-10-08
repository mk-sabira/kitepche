const ASSISTANT_URL = 'http://localhost:8000/assistant'

export async function askAssistant({ text, question, language }) {
  const response = await fetch(ASSISTANT_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, question, language }),
  })


    const data = await response.json().catch(() => null)

    if (!response.ok) {
        const detail = data?.detail
        const message = 
            typeof detail === 'string'
            ? detail
            : 'Could not get an answer. Please try again.'
        throw new Error(message)
    }
    return data

}