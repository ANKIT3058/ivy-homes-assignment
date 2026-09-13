import { getCollection } from './client'
export const getProjects = (token, params) => getCollection('/v1/projects', token, params)
