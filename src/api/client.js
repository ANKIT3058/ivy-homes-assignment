const baseUrl = import.meta.env.VITE_API_BASE_URL || import.meta.env.IVY_BASE_URL || 'https://solve.ivy.homes'
const apiKey = import.meta.env.VITE_API_KEY || import.meta.env.IVY_API_KEY

export class ApiError extends Error {
  constructor(message, status) { super(message); this.status = status }
}

export async function request(path, { method = 'GET', body, token, params } = {}) {
  const url = new URL(path, baseUrl)
  Object.entries(params || {}).forEach(([key, value]) => {
    if (value !== '' && value !== undefined && value !== null) url.searchParams.set(key, value)
  })
  const headers = { 'Content-Type': 'application/json' }
  if (apiKey) headers['X-API-Key'] = apiKey
  if (token) headers.Authorization = `Bearer ${token}`
  let response
  try { response = await fetch(url, { method, headers, body: body ? JSON.stringify(body) : undefined }) }
  catch { throw new ApiError('Unable to reach Ivy Homes. Please check your connection and try again.') }
  const data = await response.json().catch(() => null)
  if (!response.ok) throw new ApiError(data?.detail || data?.message || 'Something went wrong. Please try again.', response.status)
  return data
}

export const getCollection = (path, token, params) => request(path, { token, params })
