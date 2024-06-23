import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import RegisterPage from '../views/RegisterPage.vue'
import LoginPage from '@/views/LoginPage.vue'
import CreateCategory from '@/views/CreateCategory.vue'
import UpdateCategory from '@/views/UpdateCategory.vue'
import AllCategories from '@/views/AllCategories.vue'
import ViewCart from '@/views/ViewCart.vue'
import AdminReport from '@/views/AdminReport.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/admin-report',
    name: 'admin-report',
    component: AdminReport
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterPage
  },
  {
    path: '/login',
    name: 'login',
    component: LoginPage
  },
  {
    path: '/create-category',
    name: 'create-category',
    component: CreateCategory
  },
  {
    path: '/update-category/:id',
    name: 'update-category',
    component: UpdateCategory
  },
  {
    path: '/all-categories',
    name: 'all-categories',
    component: AllCategories
  },
  {
    path: '/view-cart',
    name: 'view-cart',
    component: ViewCart
  },
  {
    path: '/test',
    name: 'test',
    component: () => import('../views/ImageTest.vue')
  },
  {
    path: '/test2',
    name: 'test2',
    component: () => import('../views/ImageGallery.vue')
  },
  {
    path: '/about',
    name: 'about',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/AboutView.vue')
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
