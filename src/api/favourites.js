import { request } from './client'
// Live API contract: saved listings use /v1/saved and require listing_id on creation.
export const getFavourites = (token) => request('/v1/saved', { token })
export const saveFavourite = (id, token) => request('/v1/saved', { method: 'POST', body: { listing_id: id }, token })
export const removeFavourite = (id, token) => request(`/v1/saved/${encodeURIComponent(id)}`, { method: 'DELETE', token })
