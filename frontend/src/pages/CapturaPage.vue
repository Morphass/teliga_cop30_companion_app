<template>
  <q-page class="container q-pa-md position-relative green-bg">
    <q-card class="main-card">
      <q-card-section class="row no-wrap">
        <div class="col-7 card-image relative-position">
          <q-img :src="item?.imagem" class="main-img" />
          <transition name="fade">
            <img v-if="mostrarBonk" src="/effects/bonk.gif" class="bonk-animacao" />
          </transition>
          <transition name="fade">
            <img v-if="mostrarOvo" src="/effects/ovo.gif" class="ovo-animacao" />
          </transition>
        </div>

          <q-card-section class="col-5 actions-col column" style="height: 100%; align-items: flex-start;">
            <div class="row items-center q-mb-md">
              <q-icon name="backpack" color="green-8" size="28px" class="q-mr-sm" />
              <span class="text-h5" style="color:#166534; font-weight: 700;">Capturar</span>
            </div>

            <div style="flex-grow:1;"></div>

            <div class="column full-width">
              <q-btn label="Conversar" color="green" icon="chat" @click="abrirConversa" class="full-width q-mb-sm" />
              <q-btn label="Atacar" color="red" icon="bolt" @click="atacar" class="full-width q-mb-sm" />
              <q-btn label="Ovo" color="orange" icon="egg" @click="usarOvo" class="full-width" />
            </div>
          </q-card-section>
      </q-card-section>

      <q-card-section class="q-mt-md">
        <q-linear-progress
          :value="chance / 100"
          color="green-5"
          track-color="green-2"
          size="30px"
          class="progress-bar"
        >
          <div class="progress-text">{{ chance }}%</div>
        </q-linear-progress>

        <q-btn
          v-if="chance >= 100"
          label="Capturar"
          color="primary"
          class="q-mt-md full-width"
          @click="capturar"
        />
      </q-card-section>
    </q-card>

    <q-dialog v-model="mostrarDialogo" persistent>
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">{{ questao?.pergunta }}</div>
        </q-card-section>

        <q-separator />

        <q-card-section>
          <q-list bordered>
            <q-item
              clickable
              v-for="(opcao, letra) in opcoes"
              :key="letra"
              @click="responder(letra)"
            >
              <q-item-section>{{ letra }}) {{ opcao }}</q-item-section>
            </q-item>
          </q-list>
        </q-card-section>
      </q-card>

      <q-card v-if="resultado" class="q-mt-md">
        <q-card-section>
          <div :class="{ 'text-positive': resultado.acertou, 'text-negative': !resultado.acertou }">
            {{ resultado.acertou ? 'Você acertou!' : 'Errou! 😢' }}
          </div>
          <div v-if="resultado.resposta_correta">
            Resposta correta: {{ resultado.resposta_correta }}
          </div>
        </q-card-section>
        <q-card-actions align="center">
          <q-btn flat label="Fechar" color="primary" @click="fecharDialogo" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="mostrarSucessoRPG" persistent transition-show="scale" transition-hide="scale">
      <q-card class="bg-green-1 text-center q-pa-lg" style="width: 300px">
        <q-icon name="stars" color="orange" size="50px" class="q-mb-md" />
        <div class="text-h5 text-green-9 text-weight-bold">Sucesso!</div>
        <div class="text-subtitle1 text-grey-8 q-mb-lg">{{ item?.nome }} foi capturado.</div>
        
        <div class="row justify-center q-gutter-sm q-mb-lg">
            <q-badge color="red" class="q-pa-sm">
                <q-icon name="favorite" size="xs" class="q-mr-xs" />
                Vida {{ statsGanhos.bonus_vida }}
            </q-badge>
            <q-badge color="blue" class="q-pa-sm">
                <q-icon name="flash_on" size="xs" class="q-mr-xs" />
                Atq {{ statsGanhos.bonus_ataque }}
            </q-badge>
        </div>

        <q-btn label="Continuar" color="green-8" class="full-width" @click="finalizarCaptura" />
      </q-card>
    </q-dialog>

  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from 'boot/axios'
import { useQuasar } from 'quasar'

const $q = useQuasar()
const route = useRoute()
const router = useRouter()

// Dados do item e chance
const item = ref(null)
const chance = ref(0)

// Animações
const mostrarBonk = ref(false)
const mostrarOvo = ref(false)
const somBonk = ref(null)
const mostrarDialogo = ref(false)
const mostrarSucessoRPG = ref(false) 
const statsGanhos = ref({ bonus_vida: '+0', bonus_ataque: '+0' }) 
const questao = ref(null)
const resultado = ref(null)
const opcoes = ref({})

onMounted(async () => {
  somBonk.value = new Audio('/sounds/bonk.mp3')
  somBonk.value.volume = 0.8

  const itemId = route.params.id
  if (itemId) {
    const [resItem, resCaptura] = await Promise.all([
      api.get(`/api/item/${itemId}/`),
      api.get(`/api/captura/${itemId}/`)
    ])
    item.value = resItem.data
    chance.value = resCaptura.data.chance
  }
})

async function executarAcao(acao) {
  try {
    const itemId = route.params.id
    const res = await api.post(`/api/captura/${itemId}/`, { acao })
    chance.value = res.data.chance
  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao executar ação' })
  }
}

async function atacar() {
  try {
    somBonk.value.play().catch(err => console.warn('Erro ao tocar som:', err))
    mostrarBonk.value = true
    setTimeout(() => (mostrarBonk.value = false), 800)
    await executarAcao('atacar')
  } catch (err) {
    console.error(err)
  }
}

async function usarOvo() {
  try {
    mostrarOvo.value = true
    setTimeout(() => (mostrarOvo.value = false), 1000)
    await executarAcao('atacar') 
  } catch (err) {
    console.error(err)
  }
}

async function capturar() {
  try {
    const itemId = route.params.id
    const res = await api.post(`/api/captura/${itemId}/confirmar/`) 
    chance.value = 100

    if (res.data.bonus_vida && res.data.bonus_ataque) {
        statsGanhos.value = {
            bonus_vida: res.data.bonus_vida,
            bonus_ataque: res.data.bonus_ataque
        }
        mostrarSucessoRPG.value = true
    } else {
        $q.notify({ type: 'positive', message: 'Item capturado!' })
        router.push({ name: 'mapa' }) 
    }
  
  } catch(err) {
    console.error("Erro ao capturar:", err)
    $q.notify({ type: 'negative', message: 'Erro ao confirmar a captura' })
  }
}

function finalizarCaptura() {
    mostrarSucessoRPG.value = false
    router.push({ name: 'mapa' }) 
}

async function abrirConversa() {
  try {
    const itemId = route.params.id
    const res = await api.get(`/api/questao/item/${itemId}/`)
    questao.value = res.data
    opcoes.value = {
      A: res.data.escolha_a,
      B: res.data.escolha_b,
      C: res.data.escolha_c
    }
    mostrarDialogo.value = true
    resultado.value = null
  } catch (err) {
    console.error(err)
    $q.notify({ type: 'negative', message: 'Erro ao buscar questão' })
  }
}

async function responder(letra) {
  try {
    const res = await api.post(`/api/questao/${questao.value.id}/`, { resposta: letra })
    resultado.value = res.data

    if (res.data.acertou) {
      await executarAcao('conversar')
    }
  } catch (err) {
    console.error(err)
    $q.notify({ type: 'negative', message: 'Erro ao enviar resposta' })
  }
}


function fecharDialogo() {
  mostrarDialogo.value = false
  resultado.value = null
}
</script>



<style scoped>

.main-card {
  max-width: 700px;
  margin: auto;
  border-radius: 16px;
  padding: 16px;
  background-color: #ffffff; 
  display: flex;
  flex-direction: column;
}


.card-image { position: relative; max-height: 400px; }
.main-img { width: 100%; height: 100%; object-fit: cover; border-radius: 12px; }
.bonk-animacao, .ovo-animacao { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); width:150px; pointer-events:none; }
.fade-enter-active,.fade-leave-active { transition: opacity .5s; }
.fade-enter-from,.fade-leave-to { opacity:0; }
.actions-col { display:flex; flex-direction:column; gap:8px; align-items:center; justify-content:center; }
.progress-bar { position:relative; margin-top:12px; height:40px; }
.progress-text { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); font-weight:bold; color:rgb(119, 119, 119); }
.full-width { width:100%; }
</style>