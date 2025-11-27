<template>
  <q-page class="register-page">
    <div class="register-container">

      <div class="title-container">
        <h1 class="title-te-liga pixel-title">Te liga!</h1>
      </div>

      <q-card class="register-card pixel-card">
        <div class="pixel-bg" aria-hidden="true"></div>
        <div class="pixel-corners" aria-hidden="true"></div>

        <q-card-section>
          <h2 class="text-center text-dark text-h6 q-mb-sm">
            Criar uma nova conta
          </h2>

          <q-input outlined label="Nome de usuário" dense class="q-mb-md pixel-field" v-model="username" />

          <div>
            <q-input outlined label="Email" dense class="q-mb-md pixel-field" v-model="email" />
          </div>

          <q-input outlined type="password" label="Crie uma Senha" dense class="q-mb-md pixel-field" v-model="password" />
          <q-input outlined type="password" label="Confirme sua Senha" dense class="q-mb-md pixel-field" v-model="confirmPassword" />

          <div class="flex flex-center">
            <q-btn
              rounded
              label="Cadastre-se"
              class="register-btn pixel-btn"
              unelevated
              @click="handleRegister"
              text-color="black"
            />
          </div>
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<script>
import 'src/css/register.scss'
import { api } from 'boot/axios'

export default {
  name: 'RegisterPage',
  data () {
    return {
      gender: 'masculino',
      username: '',
      day: '',
      month: '',
      year: '',
      email: '',
      telefone: '',
      password: '',
      confirmPassword: ''
    }
  },
  methods: {
    async handleRegister () {
      if (!this.email || !this.username || !this.password) {
        this.$q.notify({
          color: 'negative',
          position: 'top',
          message: 'Por favor, preencha todos os campos obrigatórios.'
        })
        return
      }
      if (this.password !== this.confirmPassword) {
        this.$q.notify({
          color: 'negative',
          position: 'top',
          message: 'As senhas não coincidem.'
        })
        return
      }

      const genderMap = { masculino: 'M', feminino: 'F', outro: 'O' }

      const payload = {
        username: this.username,
        email: this.email,
        telefone: this.telefone || null,
        password1: this.password,
        password2: this.confirmPassword,
        genero: genderMap[this.gender],
        data_nas: this.year && this.month && this.day
          ? `${this.year}-${String(this.month).padStart(2, '0')}-${String(this.day).padStart(2, '0')}`
          : null
      }

      try {
        await api.post('/api/auth/registration/', payload)

        this.$q.notify({
          color: 'positive',
          position: 'top',
          message: 'Cadastro realizado com sucesso! Redirecionando para o login...'
        })

        setTimeout(() => {
          this.$router.push('/login')
        }, 2000)
      } catch (error) {
        let errorMessage = 'Ocorreu um erro no cadastro. Tente novamente.'
        const errorData = error.response?.data

        if (errorData) {
          if (typeof errorData === 'string') {
            errorMessage = errorData
          } else if (typeof errorData === 'object') {
            // Erros DRF: { campo: ['mensagem'] }
            const errorList = Object.entries(errorData).map(([key, value]) => {
              const messages = Array.isArray(value) ? value.join(', ') : value
              return `${key}: ${messages}`
            })
            if (errorList.length) errorMessage = errorList.join('\n')
          }
        } else if (error.message) {
          errorMessage = error.message
        }

        this.$q.notify({
          color: 'negative',
          position: 'top',
          message: errorMessage.replace(/\n/g, '<br>'),
          html: true
        })
      }
    }
  }
}
</script>

<style scoped>
:root{ --accent:#3b82f6; --ink:#0a1b0d }
.register-page{
  background: transparent !important;
  display: flex; align-items: center; justify-content: center;
  min-height: calc(100vh - 0px);
  padding: 24px 12px;
  position: relative; z-index: 1;
}
:global(body),
:global(#q-app),
:global(.q-layout),
:global(.q-page-container),
:global(.q-page){
  background: transparent !important;
}

.register-container{ width: min(520px, 92vw); }

.title-te-liga{
  text-align: center; margin: 0 0 8px; font-weight: 800; letter-spacing: .2px; color: var(--ink);
}
.pixel-title{
  text-shadow: 2px 2px 0 #0002, 4px 4px 0 #0001;
}

.register-card{
  background: rgba(255,255,255,.88);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  border-radius: 6px; box-shadow: 0 10px 30px rgba(0,0,0,.12);
  border: 2px solid #111; position: relative; overflow: hidden;
}
.pixel-card{ border-radius: 6px }
.pixel-bg{
  position:absolute; inset:0; pointer-events:none; opacity:.10; mix-blend-mode:multiply;
  background:
    linear-gradient(to right, #000 1px, transparent 1px) 0 0 / 8px 8px,
    linear-gradient(to bottom, #000 1px, transparent 1px) 0 0 / 8px 8px;
}
.pixel-corners::before,
.pixel-corners::after{
  content:""; position:absolute; width:10px; height:10px; background:#111;
  box-shadow:
    calc(100% - 10px) 0 0 #111,
    0 calc(100% - 10px) 0 #111,
    calc(100% - 10px) calc(100% - 10px) 0 #111;
}
.pixel-corners::before{ top:0; left:0 }
.pixel-corners::after{ display:none }

:deep(.q-input .q-field__control){
  border-radius: 0 !important;
  border: 2px solid #111 !important;
  background: #fff !important;
  box-shadow: 3px 3px 0 #1112 !important;
}
.pixel-field :deep(.q-field__control:focus-within){
  outline: 3px solid var(--accent) !important;
  box-shadow: 3px 3px 0 #111, 0 0 0 3px var(--accent) inset !important;
}

.pixel-radios :deep(.q-radio__inner){
  width: 18px; height: 18px; border: 2px solid #111; border-radius: 0;
  box-shadow: 2px 2px 0 #1112; background: #fff;
}
.pixel-radios :deep(.q-radio__inner--truthy){
  background: var(--accent); border-color: #111;
}
.pixel-radios :deep(.q-radio__bg){
  display:none;
}

.register-btn.pixel-btn{
  background: var(--accent);
  color: #fff;
  font-weight: 900;
  padding: 10px 20px;
  border-radius: 0;
  border: 2px solid #111;
  box-shadow: 4px 4px 0 #111;
  transition: transform .05s linear, box-shadow .05s linear;
}
.register-btn.pixel-btn:active{
  transform: translate(2px,2px);
  box-shadow: 2px 2px 0 #111;
}

.pixel-link{
  color: #0b3b22; text-decoration: none; border-bottom: 2px solid currentColor; padding-bottom: 1px;
}
</style>
