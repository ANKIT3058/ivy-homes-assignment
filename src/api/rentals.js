import { getCollection } from './client'
export const getRentals = (token, params) => getCollection('/v1/rentals', token, params)
