<template>
  <q-page class="profile-page">
    <div class="profile-header q-pa-md">
      <h1 class="text-h4 q-mb-xs">Te liga!</h1>
      <div class="row items-center cursor-pointer" @click="$router.push('/mapa')">
        <q-icon name="arrow_back" size="20px" />
        <span class="text-subtitle2 q-ml-xs">Voltar ao mapa</span>
      </div>
    </div>

    <div class="flex flex-center q-pa-md q-md-pa-lg">
      
      <q-card class="profile-card">
        <h1 class="text-h5 text-green-10 text-center q-mb-lg">Perfil</h1>

        <div class="row items-center justify-center q-mb-lg">
          <q-avatar size="80px" class="q-mr-md">
            <img :src="user.avatar || 'https://cdn-icons-png.flaticon.com/512/847/847969.png'" />
          </q-avatar>
          <div>
            <div class="text-green-10 user-name">{{ user.username }}</div>
            <div class="text-grey-7">{{ user.email }}</div>
          </div>
        </div>

        <div class="q-gutter-md info-container">
          <div class="perfil-campo">
            <span class="campo-label">Nome</span>
            <span class="campo-valor">{{ user.username }}</span>
          </div>
          <div class="perfil-campo">
            <span class="campo-label">Email</span>
            <span class="campo-valor">{{ user.email }}</span>
          </div>
          <div class="perfil-campo">
            <span class="campo-label">Idade</span>
            <span class="campo-valor">{{ user.idade }}</span>
          </div>
          <div class="perfil-campo">
            <span class="campo-label">Telefone</span>
            <span class="campo-valor">{{ user.telefone }}</span>
          </div>
        </div>

        <div class="column items-center q-mt-xl q-gutter-md action-buttons">
          <q-btn label="Editar perfil" color="green-10" class="full-width" rounded @click="editarPerfil" />
          <q-btn label="Alterar senha" color="green-10" class="full-width" rounded @click="abrirAlterarSenha" />
          <q-btn label="Excluir conta" color="purple-10" class="full-width" rounded @click="confirmarExclusao" />
        </div>
      </q-card>
    </div>

    <q-dialog v-model="senhaDialog">
      <q-card>
        <q-card-section>
          <div class="text-h6">Alterar senha</div>
          <q-input v-model="oldPassword" label="Senha atual" type="password" dense />
          <q-input v-model="newPassword" label="Nova senha" type="password" dense />
          <q-input v-model="confirmPassword" label="Confirme a nova senha" type="password" dense />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="grey" v-close-popup @click="senhaDialog=false" />
          <q-btn flat label="Alterar" color="green-10" @click="alterarSenha" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="excluirDialog">
      <q-card>
        <q-card-section>
          <div class="text-h6">Excluir conta</div>
          <div>Tem certeza que deseja excluir sua conta? Esta ação não poderá ser desfeita.</div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="grey" v-close-popup />
          <q-btn flat label="Excluir" color="purple-10" @click="excluirConta" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from 'boot/axios'
import { LocalStorage, useQuasar } from 'quasar'
import 'src/css/profile.scss' 

const $q = useQuasar()
const router = useRouter()

const user = ref({ username:'', email:'', idade:'', telefone:'', avatar:null })
const excluirDialog = ref(false)
const senhaDialog = ref(false)
const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')

onMounted(async () => {
  try {
    const token = LocalStorage.getItem('user_token')
    if (!token) { router.push('/login'); return }

    const { data } = await api.get('/api/auth/user/')
    user.value.username = data.username
    user.value.email = data.email
    user.value.idade = calcularIdade(data.data_nas)
    user.value.telefone = data.telefone || ''
    user.value.avatar = data.avatar || null
  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao carregar perfil' })
    router.push('/login')
  }
})

function calcularIdade(data_nas) {
  if (!data_nas) return ''
  const nascimento = new Date(data_nas)
  const hoje = new Date()
  let idade = hoje.getFullYear() - nascimento.getFullYear()
  const m = hoje.getMonth() - nascimento.getMonth()
  if (m < 0 || (m === 0 && hoje.getDate() < nascimento.getDate())) idade--
  return idade
}

function editarPerfil() {
  $q.notify({ type: 'info', message: 'Função de edição de perfil ainda não implementada' })
}

function abrirAlterarSenha() {
  senhaDialog.value = true
}

async function alterarSenha() {
  if (newPassword.value !== confirmPassword.value) {
    $q.notify({ type:'negative', message:'As novas senhas não coincidem' })
    return
  }

  try {
    await api.put('/api/users/me/change_password/', {
      old_password: oldPassword.value,
      new_password: newPassword.value
    })
    $q.notify({ type:'positive', message:'Senha alterada com sucesso' })
    senhaDialog.value = false
    oldPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
  } catch (e) {
    const msg = e.response?.data?.old_password || 'Erro ao alterar senha'
    $q.notify({ type:'negative', message: msg })
  }
}

function confirmarExclusao() { excluirDialog.value = true }

async function excluirConta() {
  try {
    await api.delete('/api/users/me/delete/')
    LocalStorage.remove('user_token')
    LocalStorage.remove('user_data')
    router.push('/login')
    $q.notify({ type:'positive', message:'Conta excluída com sucesso' })
  } catch (e) {
    console.error(e)
    $q.notify({ type:'negative', message:'Erro ao excluir conta' })
  }
  excluirDialog.value = false
}
</script>

<style scoped>
.profile-header {
  padding-top: 16px;
  padding-bottom: 8px;
  position: relative; 
  z-index: 10;     
}

.profile-page {
  min-height: 100vh;
  overflow-x: hidden;
}

.profile-header h1 {
  color: white !important;
  text-shadow: 0 1px 3px rgba(0,0,0,0.3);
}

.profile-header .q-icon,
.profile-header .text-subtitle2 {
  color: white !important;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.profile-card {
  width: 100%;
  max-width: 500px;
  border-radius: 16px;
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 24px; 
}

@media (min-width: 600px) { 
  .profile-card {
    padding: 32px;
  }
}


.profile-card h1 {
  color: #2e7d32 !important;
}

.user-name {
  font-weight: bold;
  font-size: 1.2rem;
  color: #2e7d32 !important;
}

.text-grey-7 {
  color: #757575 !important;
}

.perfil-campo {
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
  margin-bottom: 16px; 
}

.campo-label {
  display: block; 
  font-weight: 600;
  color: #2e7d32; 
  font-size: 0.9rem;
  margin-bottom: 2px;
}

.campo-valor {
  display: block;
  color: #333; 
  font-size: 1.1rem;
}

.action-buttons .q-btn {
  height: 48px;
  font-weight: 600;
}
</style>