import { defineRouter } from '#q-app/wrappers'
import {
  createRouter,
  createMemoryHistory,
  createWebHistory,
  createWebHashHistory,
} from 'vue-router'
import routes from './routes'

export default defineRouter(function () {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : process.env.VUE_ROUTER_MODE === 'history'
    ? createWebHistory
    : createWebHashHistory

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,
    history: createHistory(process.env.VUE_ROUTER_BASE),
  })

  // ✅ Proteção de rotas ATUALIZADA para usar localStorage
  Router.beforeEach((to, from, next) => {
    // 2. BUSCAR DADOS DIRETAMENTE DO LOCALSTORAGE
    const token = localStorage.getItem('user_token')
    const userDataString = localStorage.getItem('user_data')

    // **** LINHA CORRIGIDA ****
    // Verifica se a string não é nula E não é a palavra "undefined"
    const user = (userDataString && userDataString !== 'undefined')
                 ? JSON.parse(userDataString)
                 : null
    // **** FIM DA CORREÇÃO ****

    const isAuthenticated = !!token

    // 3. VERIFICAR SE A ROTA EXIGE AUTENTICAÇÃO
    if (to.meta.requiresAuth && !isAuthenticated) {
      // Se a rota é protegida e não há token, redireciona para o login
      return next('/login')
    }

    // 4. VERIFICAR SE A ROTA EXIGE PERMISSÃO DE ADMIN
    // (o campo is_staff vem dos dados do usuário salvos no localStorage)
    if (to.meta.requiresAdmin && (!user || !user.is_staff)) {
      // Se a rota exige admin e o usuário não é staff, redireciona para a home
      return next('/')
    }

    // Se passou por todas as verificações, permite o acesso
    next()
  })

  return Router
})