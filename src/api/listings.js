import { getCollection, request } from './client'
export const getListings = (token, params) => getCollection('/v1/listings', token, params)
export const getListing = (id, token) => request(`/v1/listings/${encodeURIComponent(id)}`, { token })
