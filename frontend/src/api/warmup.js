import { API_URL } from './config'

// Fire-and-forget request that wakes the sleeping backend while the visitor
// is still looking at the page. Errors are ignored on purpose.
export function warmUpServer() {
  fetch(`${API_URL}/health`).catch(() => {})
}