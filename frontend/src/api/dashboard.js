import request from './request'

export const getOverview = () => request.get('/dashboard/overview')
export const getPartnerDistribution = () => request.get('/dashboard/partner-distribution')
export const getProjectFunnel = () => request.get('/dashboard/project-funnel')
export const getContractTrend = (monthCount) => request.get('/dashboard/contract-trend', { params: { month_count: monthCount } })
export const getQualificationAlerts = (days) => request.get('/dashboard/qualification-alerts', { params: { days } })
export const getRecentActivity = (limit) => request.get('/dashboard/recent-activity', { params: { limit } })
export const getPaymentMilestones = () => request.get('/dashboard/payment-milestones')