// Retries a request when the server is still waking up: a network error
// or a 502/503/504 answer. Use it for GET requests only.
const RETRY_STATUSES = [502, 503, 504]

export async function fetchWithRetry(
  url,
  options = {},
  { tries = 8, delayMs = 5000, onRetry } = {},
) {
  for (let attempt = 1; ; attempt++) {
    try {
      const response = await fetch(url, options)
      if (!RETRY_STATUSES.includes(response.status) || attempt >= tries) {
        return response
      }
    } catch (error) {
      if (attempt >= tries) throw error
    }
    if (onRetry) onRetry(attempt)
    await new Promise((resolve) => setTimeout(resolve, delayMs))
  }
}
