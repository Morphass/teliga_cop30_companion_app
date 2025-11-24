import { boot } from 'quasar/wrappers'
import axios from 'axios'
import { Notify, Platform } from 'quasar'


const PROD_API_URL = 'https://teliga-backend.onrender.com' 
const DEV_ANDROID_URL = 'http://10.0.2.2:8000'
const DEV_WEB_URL = 'http://127.0.0.1:8000'


function getBaseUrl() {
  if (import.meta.env.DEV) {
    // Desenvolvimento

    if (Platform.is.capacitor) {
      // Rodando no Emulador/Celular
      console.log('Rodando em DEV (Capacitor). API em: ' + DEV_ANDROID_URL)
      return DEV_ANDROID_URL
    } else {
      // Rodando no Navegador Desktop
      console.log('Rodando em DEV (Web). API em: ' + DEV_WEB_URL)
      return DEV_WEB_URL
    }
  } else {
    // Produção
    console.log('Rodando em PROD. API em: ' + PROD_API_URL)
    return PROD_API_URL
  }
}

if (PROD_API_URL.includes('COLOQUE_SUA_URL') || !PROD_API_URL.startsWith('https://')) {
  console.error("ERRO DE CONFIGURAÇÃO: Por favor, atualize a PROD_API_URL em src/boot/axios.js")
  Notify.create({
    message: 'ERRO: API URL de Produção não configurada.',
    color: 'negative',
    position: 'top',
    icon: 'report_problem'
  })
}

const api = axios.create({
  baseURL: getBaseUrl() 
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('user_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, error => {
  return Promise.reject(error)
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401 && error.response.data?.code === 'token_not_valid') {
      
      localStorage.removeItem('user_token')
      localStorage.removeItem('user_data')

      Notify.create({
        message: 'Sua sessão expirou. Por favor, faça o login novamente.',
        color: 'warning',
        icon: 'warning',
        position: 'top'
      })
      
      window.location.href = '/#/login'
    }
    return Promise.reject(error)
  }
)

export async function syncLocalMochilaToBackend() {
  try {
    const token = localStorage.getItem('user_token')
    if (!token) {
      return
    }

    const possibleKeys = ['mochila', 'mochila_eventos', 'mochila_itens', 'mochila_pocoes']
    let combined = []

    for (const key of possibleKeys) {
      try {
        const raw = localStorage.getItem(key)
        if (!raw || raw === "undefined") continue
        const parsed = JSON.parse(raw)
        if (Array.isArray(parsed)) combined = combined.concat(parsed)
      } catch (e) {
        console.warn(`Não foi possível parsear ${key}:`, e)
      }
    }

    if (combined.length === 0) return
    for (const entry of combined) {
      try {
        if (entry.evento_id || entry.tipoConteudo === 'evento' || entry.tipo === 'EVENT') {
          const eventoId = entry.evento_id ?? entry.id
          if (eventoId) {
            await api.post('/api/capturas/eventos/', { evento_id: eventoId })
          }
          continue
        }

        if (entry.item_id || entry.tipoConteudo === 'item' || (entry.tipo && entry.tipo !== 'POC')) {
          const itemId = entry.item_id ?? entry.id
          if (itemId) {
            await api.post('/api/capturas/items/', { item_id: itemId })
          }
          continue
        }

        if (entry.pocao_id || entry.tipo === 'POC' || entry.tipoConteudo === 'pocao') {
          const pocaoId = entry.pocao_id ?? entry.id
          if (pocaoId) {
            await api.post('/api/capturas/pocoes/', { pocao_id: pocaoId })
          } else {
            if (entry.id) await api.post('/api/capturas/pocoes/', { pocao_id: entry.id })
          }
          continue
        }

        if (entry.id) {
          await api.post('/api/capturas/items/', { item_id: entry.id })
        }
      } catch (e) {
        console.warn('Falha ao migrar entry para backend (seguindo adiante):', e, entry)
      }
    }

    for (const key of possibleKeys) {
      localStorage.removeItem(key)
    }

    localStorage.removeItem('mochila')
    Notify.create({
      message: 'Mochila sincronizada com o servidor.',
      color: 'positive',
      position: 'top'
    })
  } catch (err) {
    console.error('Erro ao sincronizar localStorage com backend:', err)
    Notify.create({
      message: 'Problema ao sincronizar a mochila. Alguns itens podem não ter sido migrados.',
      color: 'warning',
      position: 'top'
    })
  }
}

export default boot(({ app }) => {
  app.config.globalProperties.$api = api
})

export { api }