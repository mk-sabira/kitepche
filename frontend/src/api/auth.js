import { API_URL } from './config'


const AUTH_URL = `${API_URL}/auth`


function errorMessage(data, fallback) {
  const detail = data?.detail
  if (typeof detail === 'string') return detail
  // validation errors (422) arrive as a list; show the first message
  if (Array.isArray(detail) && detail.length > 0 && detail[0].msg) {
    return detail[0].msg.replace(/^Value error, /, '')
  }
  return fallback
}

function toError(response, data, fallback) {
  const error = new Error(errorMessage(data, fallback))
  error.status = response.status
  return error
}

export async function registerUser(email, password) {
  const response = await fetch(`${AUTH_URL}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  const data = await response.json().catch(() => null)
  if (!response.ok) {
    throw toError(response, data, 'Could not create the account. Please try again.')
  }
  return data
}

export async function loginUser(email, password) {
  // the backend's login takes a form, and the email goes in the "username" field
  const response = await fetch(`${AUTH_URL}/login`, {
    method: 'POST',
    credentials: 'include',
    body: new URLSearchParams({ username: email, password }),
  })
  const data = await response.json().catch(() => null)
  if (!response.ok) {
    throw toError(response, data, 'Could not log in. Please try again.')
  }
  return data
}

export async function fetchMe() {
  const response = await fetch(`${AUTH_URL}/me`, {
    credentials: 'include',
  })
  const data = await response.json().catch(() => null)
  if (!response.ok) {
    throw toError(response, data, 'Could not load your account.')
  }
  return data
}



export async function logoutUser() {
  const response = await fetch(`${AUTH_URL}/logout`, {
    method: 'POST',
    credentials: 'include',
  })
  if (!response.ok) {
    throw toError(response, null, 'Could not log out. Please try again.')
  }
}

