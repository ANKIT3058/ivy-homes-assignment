import { request } from './client'
export const login = (email, password) => request('/auth/login', { method: 'POST', body: { email, password } })
export const logout = (token) => request('/auth/logout', { method: 'POST', token })
