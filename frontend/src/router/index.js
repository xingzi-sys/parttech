import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue')
      },
      {
        path: 'partners',
        name: 'Partners',
        component: () => import('@/views/partners/PartnerList.vue')
      },
      {
        path: 'partners/:id',
        name: 'PartnerDetail',
        component: () => import('@/views/partners/PartnerDetail.vue')
      },
      {
        path: 'contacts',
        name: 'Contacts',
        component: () => import('@/views/contacts/ContactList.vue')
      },
      {
        path: 'products',
        name: 'Products',
        component: () => import('@/views/products/ProductList.vue')
      },
      {
        path: 'projects',
        name: 'Projects',
        component: () => import('@/views/projects/ProjectList.vue')
      },
      {
        path: 'projects/:id',
        name: 'ProjectDetail',
        component: () => import('@/views/projects/ProjectDetail.vue')
      },
      {
        path: 'contracts',
        name: 'Contracts',
        component: () => import('@/views/contracts/ContractList.vue')
      },
      {
        path: 'contracts/:id',
        name: 'ContractDetail',
        component: () => import('@/views/contracts/ContractDetail.vue')
      },
      {
        path: 'followups',
        name: 'Followups',
        component: () => import('@/views/followups/FollowupList.vue')
      },
      {
        path: 'business-terms',
        name: 'BusinessTerms',
        component: () => import('@/views/business-terms/BusinessTermList.vue')
      },
      {
        path: 'qualifications',
        name: 'Qualifications',
        component: () => import('@/views/qualifications/QualificationList.vue')
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/admin/UserList.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.path !== '/login' && !authStore.token) {
    next('/login')
  } else if (to.path === '/login' && authStore.token) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router