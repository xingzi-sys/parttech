import request from './request'

export const getPartners = (params) => request.get('/partners', { params })
export const getPartner = (id) => request.get(`/partners/${id}`)
export const createPartner = (data) => request.post('/partners', data)
export const updatePartner = (id, data) => request.put(`/partners/${id}`, data)
export const deletePartner = (id) => request.delete(`/partners/${id}`)
export const getPartnerOptions = () => request.get('/partners/options')
export const getPartnerTypes = () => request.get('/partners/types')
export const getPartnerLevels = () => request.get('/partners/levels')
export const getPartnerStatuses = () => request.get('/partners/statuses')