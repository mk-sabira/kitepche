const ASSISTANT_URL = 'http://localhost:8000/assistant'

export async function askAssistant({ text, question, language, token }) {
  const response = await fetch(ASSISTANT_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ text, question, language }),
  })

  const data = await response.json().catch(() => null)

  if (!response.ok) {
    const detail = data?.detail
    const message =
      typeof detail === 'string'
        ? detail
        : 'Could not get an answer. Please try again.'
    const error = new Error(message)
    error.status = response.status
    const retryAfter = Number(response.headers.get('Retry-After'))
    if (retryAfter > 0) error.retryAfter = retryAfter
    throw error
  }

  return data
}