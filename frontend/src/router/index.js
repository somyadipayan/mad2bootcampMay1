import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import RegisterPage from '../views/RegisterPage.vue'
import LoginPage from '@/views/LoginPage.vue'
import CreateCategory from '@/views/CreateCategory.vue'
import UpdateCategory from '@/views/UpdateCategory.vue'
import AllCategories from '@/views/AllCategories.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
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
