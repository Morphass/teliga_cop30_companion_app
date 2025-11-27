<template>
  <q-page class="login-page">
    <div class="login-grid">

      <section class="left copy hide--mobile">
        <div class="brand-badge pixel-badge">
          <span class="pin">📍</span><strong>TE LIGA!</strong>
        </div>
        <h1 class="title">
          Entre para <span>jogar</span> na cidade
        </h1>
        <ul class="benefits">
          <li><q-icon name="map" /> Explore eventos próximos</li>
          <li><q-icon name="videogame_asset" /> Ganhe pontos e conquistas</li>
          <li><q-icon name="emoji_events" /> Troque por recompensas</li>
        </ul>
      </section>

      <section class="right">
        <q-card class="login-card pixel-card">
          <div class="pixel-bg" aria-hidden="true"></div>
          <div class="pixel-corners" aria-hidden="true"></div>

          <q-card-section class="text-center q-pb-sm">
            <div class="text-h5 text-dark text-weight-bold pixel-title">Bem-vindo!</div>
            <div class="text-subtitle2 q-mt-xs">Efetue seu login</div>
          </q-card-section>

          <q-card-section class="q-pt-sm">
            <div class="row items-center pixel-divider">
              <div class="col-5"><q-separator /></div>
              <div class="col text-center text-caption text-dark">entrar com</div>
              <div class="col-5"><q-separator /></div>
            </div>
          </q-card-section>

          <q-card-section class="q-pt-none">
            <q-form @submit.prevent="handleLogin" greedy>
              <q-input
                v-model="username" label="Usuário ou Email" outlined dense class="q-mb-md pixel-field"
                :rules="[v => !!v || 'Informe seu usuário ou email']"
                autocomplete="username"
              >
                <template #prepend><q-icon name="person" /></template>
              </q-input>

              <q-input
                v-model="password" :type="showPass ? 'text' : 'password'" label="Senha" outlined dense class="q-mb-xs pixel-field"
                :rules="[v => !!v || 'Informe sua senha']"
                autocomplete="current-password"
                @keydown="onPassKey"
              >
                <template #prepend><q-icon name="lock" /></template>
                <template #append>
                  <q-icon :name="showPass ? 'visibility_off' : 'visibility'" class="cursor-pointer" @click="showPass = !showPass" />
                </template>
              </q-input>

              <div v-if="capsOn" class="caps-warning pixel-note">
                <q-icon name="keyboard_capslock" size="16px" /> Caps Lock ativado
              </div>

              <div class="row items-center q-mt-sm q-mb-md">
                <div class="col">
                  <q-toggle v-model="remember" label="Lembrar de mim" dense class="pixel-toggle" />
                </div>
              </div>

              <q-btn
                label="Acessar"
                class="btn-primary pixel-btn"
                rounded
                type="submit"
                :loading="isLoading"
                :disable="isLoading"
                text-color="black"
              />

            </q-form>

            <div class="text-center q-mt-md">
              <span class="text-caption">Novo aqui?</span>
              <q-btn flat dense class="link q-ml-xs pixel-link" to="/register">Criar conta</q-btn>
            </div>
          </q-card-section>
        </q-card>
      </section>

    </div>
  </q-page>
</template>

<script setup>
defineOptions({ name: 'LoginPage' })

import { ref } from 'vue'
import { useQuasar } from 'quasar'
import { useRouter } from 'vue-router'
import { api } from 'boot/axios'

const $q = useQuasar()
const router = useRouter()
const username = ref('')
const password = ref('')
const showPass = ref(false)
const isLoading = ref(false)
const capsOn = ref(false)
const remember = ref(true)

function onPassKey (e) {
  const getter = e.getModifierState || (() => false)
  capsOn.value = getter.call(e, 'CapsLock')
}

async function handleLogin () {
  if (!username.value || !password.value) {
    $q.notify({ color: 'warning', message: 'Por favor, preencha o usuário e a senha.', icon: 'warning' })
    return
  }

  isLoading.value = true
  try {
    const resp = await api.post('/api/auth/login/', {
      username: username.value,
      password: password.value
    })

    if (remember.value) {
      localStorage.setItem('user_token', resp.data.access)
      localStorage.setItem('user_data', JSON.stringify(resp.data.user))
    } else {
      sessionStorage.setItem('user_token', resp.data.access)
      sessionStorage.setItem('user_data', JSON.stringify(resp.data.user))
      localStorage.removeItem('user_token')
      localStorage.removeItem('user_data')
    }

    $q.notify({ color: 'positive', message: 'Login efetuado com sucesso!' })
    router.push('/')

  } catch (error) {
    let msg = 'Usuário ou senha inválidos. Tente novamente.'
    const data = error && error.response ? error.response.data : null
    if (data) {
      if (typeof data === 'string') msg = data
      else if (typeof data === 'object') {
        const list = []
        for (const k in data) {
          if (!Object.prototype.hasOwnProperty.call(data, k)) continue
          const v = data[k]
          list.push(`${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
        }
        if (list.length) msg = list.join(' | ')
      }
    }
    $q.notify({ color: 'negative', message: msg, icon: 'report_problem' })
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
:root{ --accent:#3b82f6; --ink:#0a1b0d }
.login-page{
  background: transparent !important;
  min-height: 100vh; display: grid; place-items: center; padding: 24px 16px;
}
/* grid responsivo */
.login-grid{
  width: min(1120px, 96vw);
  display: grid; grid-template-columns: 1fr 520px; gap: 24px; align-items: center;
}
@media (max-width: 900px){ .login-grid{ grid-template-columns: 1fr } .hide--mobile{ display: none } }

.copy { color: var(--ink) }
.brand-badge{
  display:inline-flex; align-items:center; gap:8px;
  background:#eafff0; color:#084a2a; font-weight:800;
  padding:6px 12px; border-radius:4px; box-shadow:0 2px 0 #0003; margin-bottom:12px;
}
.pixel-badge{ border:2px solid #111; box-shadow: 2px 2px 0 #111 }

.title{
  font-size: clamp(28px, 4.5vw, 48px); line-height: 1.05; margin: 6px 0 12px;
  text-shadow: 2px 2px 0 #0002, 4px 4px 0 #0001;
}
.title span{ color: var(--accent) }
.benefits{ list-style:none; padding:0; margin:10px 0 0; display:grid; gap:6px; font-weight:700 }
.benefits li{ display:flex; align-items:center; gap:8px }

.login-card{
  position: relative; background: rgba(255,255,255,.92);
  backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
  border-radius: 6px; box-shadow: 0 10px 30px rgba(0,0,0,.12);
  border: 2px solid #111; overflow: hidden;
}
.pixel-bg{
  position:absolute; inset:0; pointer-events:none; opacity:.12; mix-blend-mode:multiply;
  background:
    linear-gradient(to right, #000 1px, transparent 1px) 0 0 / 8px 8px,
    linear-gradient(to bottom, #000 1px, transparent 1px) 0 0 / 8px 8px;
}
.pixel-corners::before,
.pixel-corners::after{
  content:""; position:absolute; width:10px; height:10px; background:#111;
  box-shadow:
    calc(100% - 10px) 0 0 #111, /* top-right */
    0 calc(100% - 10px) 0 #111, /* bottom-left */
    calc(100% - 10px) calc(100% - 10px) 0 #111; /* bottom-right */
}
.pixel-corners::before{ top:0; left:0 }
.pixel-corners::after{ display:none } /* só precisa de um pseudo para as sombras */

.pixel-title{
  font-weight:900;
  letter-spacing: .5px; text-shadow: 2px 2px 0 #0001;
}

.pixel-field :deep(.q-field__control){
  border-radius: 0 !important;
  border: 2px solid #111 !important;
  background: #fff !important;
  box-shadow: 3px 3px 0 #1112 !important;
}
.pixel-field :deep(.q-field__control:focus-within){
  outline: 3px solid var(--accent) !important;
  box-shadow: 3px 3px 0 #111, 0 0 0 3px var(--accent) inset !important;
}

.pixel-divider .text-caption{
  text-transform: uppercase; letter-spacing: .1em; opacity:.8;
}

.pixel-icon{ image-rendering: pixelated; }
.pixel-icon-btn{
  border: 2px solid #111; border-radius: 0;
  box-shadow: 3px 3px 0 #1112;
}

.caps-warning{
  display:flex; align-items:center; gap:6px;
  color:#111; background:#ffef8a; border:2px solid #111;
  padding:6px 8px; border-radius: 0; box-shadow: 3px 3px 0 #1112;
}
.pixel-link{ text-decoration: none; border-bottom: 2px solid currentColor; padding-bottom: 1px }

.pixel-toggle :deep(.q-toggle__inner){
  border: 2px solid #111; border-radius: 0;
}
.pixel-toggle :deep(.q-toggle__thumb){
  border-radius: 0;
}

.btn-primary.pixel-btn{
  width:100%; border-radius:0; border: 2px solid #111;
  background: var(--accent); color:#fff; font-weight:900;
  padding: 10px 18px;
  box-shadow: 4px 4px 0 #111; transition: transform .05s linear, box-shadow .05s linear;
}
.btn-primary.pixel-btn:active{
  transform: translate(2px,2px);
  box-shadow: 2px 2px 0 #111;
}

:deep(.q-input .q-field__control){ background:#fff }
</style>
