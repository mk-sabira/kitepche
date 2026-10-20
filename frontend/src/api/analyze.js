import { API_URL } from './config'


const ANALYZE_URL = `${API_URL}/analyze`


export async function analyzeText(text) {
  const response = await fetch(ANALYZE_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  })

  const data = await response.json().catch(() => null)

  if (!response.ok) {
    const detail = data?.detail
    const message =
      typeof detail === 'string'
        ? detail
        : 'Could not analyze this text. Please try again.'
    throw new Error(message)
  }

  return data
}
