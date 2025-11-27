<template>
  <q-page class="container q-pa-md position-relative green-bg">
    <q-card class="main-card">
      <q-card-section class="row no-wrap">
        <div class="col-7 card-image relative-position">
          <q-img :src="item?.imagem" class="main-img" />
          <img v-if="mostrarBonk" src="/effects/bonk.gif" class="animacao-bonk" />
          <img v-if="mostrarOvo" src="/effects/ovo.gif" class="animacao-ovo" />
        </div>

        <q-card-section class="col-5 actions-col column" style="height: 100%; align-items: flex-start;">
          <div class="row items-center q-mb-md">
            <q-icon name="backpack" color="green-8" size="28px" class="q-mr-sm" />
            <span class="text-h5" style="color:#166534; font-weight: 700;">Capturar</span>
          </div>

          <div style="flex-grow:1;"></div>

          <div class="column full-width">

            <q-btn
              v-for="habilidade in habilidades"
              :key="habilidade.id"
              :label="habilidade.nome"
              color="primary"
              :disable="habilidade.quantidade === 0"
              class="full-width q-mb-sm"
              @click="usarHabilidade(habilidade)"
            >
              <template v-slot:append>
                <span v-if="habilidade.quantidade !== null" class="text-subtitle2 q-ml-sm">
                  x{{ habilidade.quantidade }}
                </span>
              </template>
            </q-btn>

            <q-separator spaced />

            <q-btn
              label="Conversar"
              color="green"
              icon="chat"
              class="full-width q-mb-sm"
              @click="abrirConversa"
              :disable="conversaUsada"
              :class="{ 'bg-grey-5': conversaUsada }"
            />

            <q-btn
              label="Soco"
              icon="sports_mma"
              color="red"
              class="full-width q-mb-sm"
              @click="usarSoco"
            />

            <q-btn
              label="Ovo 🥚"
              color="yellow"
              class="full-width q-mb-sm"
              :disable="ovoUsado"
              @click="usarOvo"
            />
            
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
          <div class="progress-text">{{ Math.round(chance) }}%</div>
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
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from 'boot/axios'
import { useQuasar } from 'quasar'

const $q = useQuasar()
const route = useRoute()
const router = useRouter()

// Dados do item e chance
const item = ref(null)
const chance = ref(0)
const mostrarSucessoRPG = ref(false)
const statsGanhos = ref({ bonus_vida: '+0', bonus_ataque: '+0' })

// lista de habilidades (vinda do backend)
const habilidades = ref([])

// Animações
const mostrarBonk = ref(false)
const mostrarOvo = ref(false)

// Diálogo de perguntas
const mostrarDialogo = ref(false)
const questao = ref(null)
const resultado = ref(null)
const opcoes = ref({})
const conversaUsada = ref(false)

/* ============================
      FUNÇÃO load()
============================= */
async function load(itemId) {
  try {
    const [resItem, resProgresso] = await Promise.all([
      api.get(`/api/item/${itemId}/`),
      api.get(`/api/captura/${itemId}/`) // <-- CORRETO
    ])

    item.value = resItem.data
    chance.value = resProgresso.data.chance
    conversaUsada.value = !!resProgresso.data.conversa_usada

    // Busca habilidades
    try {
      const resHabs = await api.get(`/api/habilidades/${itemId}/habilidades/`)
      habilidades.value = resHabs.data
    } catch (err) {
      habilidades.value = []
      console.warn("Erro ao buscar habilidades", err)
    }

  } catch (e) {
    console.error("Erro ao carregar item:", e)
    $q.notify({ type: 'negative', message: 'Erro ao carregar dados do item.' })
  }
}

/* ============================
  Carrega ao entrar na página
============================= */
onMounted(() => {
  const itemId = route.params.id
  if (itemId) load(itemId)
})

/* ============================
  Recarrega quando trocar de item
============================= */
watch(() => route.params.id, (newId) => {
  if (newId) load(newId)
})

/* ============================
      EXECUTAR HABILIDADE
============================= */
async function executarAcao(habilidade_id) {
  try {
    const itemId = route.params.id
    const res = await api.post(`/api/captura/${itemId}/`, { habilidade_id })

    if (res.data.chance !== undefined) {
      chance.value = res.data.chance
    }

    if (res.data.habilidade) {
      const h = res.data.habilidade
      const idx = habilidades.value.findIndex(x => x.id === h.id)
      if (idx !== -1) habilidades.value[idx] = { ...habilidades.value[idx], ...h }
    }
  } catch (err) {
    const msg = err?.response?.data?.detail || 'Erro ao executar ação'
    $q.notify({ type: 'negative', message: msg })
  }
}

/* ============================
        USAR HABILIDADE
============================= */
async function usarHabilidade(h) {
  if (h.quantidade === 0) {
    $q.notify({ type: 'negative', message: 'Sem usos restantes dessa habilidade.' })
    return
  }

  if (h.som) {
    const a = new Audio(h.som)
    a.play().catch(() => {})
  }

  if (h.animacao) {
    // Exemplo de animação
  }

  await executarAcao(h.id)
}

async function usarSoco() {
  try {
    const itemId = route.params.id

    const res = await api.post(`/api/captura/${itemId}/soco/`)

    chance.value = res.data.chance_atual

    $q.notify({
      type: res.data.sucesso ? 'positive' : 'negative',
      message: res.data.mensagem
    })

    // animação 
    mostrarBonk.value = true
    setTimeout(() => (mostrarBonk.value = false), 600)

    // Som
    const audio = new Audio('/sounds/bonk.mp3')
    audio.play().catch(() => {})

  } catch (err) {
    console.error(err)
    $q.notify({ type: 'negative', message: 'Erro ao usar soco' })
  }
}

async function usarOvo() {
  try {
    const itemId = route.params.id

    const res = await api.post(`/api/captura/${itemId}/usar_ovo/`)

    // Atualiza a chance imediatamente usando chance_atual
    if (res.data.chance_atual !== undefined && res.data.chance_atual !== null) {
      chance.value = res.data.chance_atual
    }

    // Mostra animação
    mostrarOvo.value = true
    setTimeout(() => (mostrarOvo.value = false), 1500)

    // Som
    const audio = new Audio('/sounds/gnomed.mp3')
    audio.play().catch(() => {})

    // Notificação
    const mensagem = res.data.sucesso ? 'Sucesso! +15%' : 'O ovo quebrou! -5%'
    $q.notify({ type: res.data.sucesso ? 'positive' : 'negative', message: mensagem })

  } catch (err) {
    console.error(err)
    $q.notify({ type: 'negative', message: 'Erro ao usar o ovo' })
  }
}

/* ============================
          CAPTURAR
============================= */
async function capturar() {
  try {
    const id = route.params.id
    const res = await api.post(`/api/captura/${id}/confirmar/`)

    // Se o endpoint retornar bônus, mostra o popup com os valores
    const hasBonus = (res.data && (res.data.bonus_vida !== undefined || res.data.bonus_ataque !== undefined))

    if (hasBonus) {
      statsGanhos.value = {
        bonus_vida: res.data.bonus_vida ?? '+0',
        bonus_ataque: res.data.bonus_ataque ?? '+0'
      }
      // mostra o diálogo de sucesso 
      mostrarSucessoRPG.value = true
      chance.value = 0
    } else {
      $q.notify({ type: 'positive', message: res.data.mensagem || 'Item capturado!' })
      router.push({ name: 'mapa' })
    }
  } catch (err) {
    console.error("Erro ao capturar:", err)
    const msg = err?.response?.data?.error || 'Erro ao confirmar a captura'
    $q.notify({ type: 'negative', message: msg })
  }
}


/* ============================
          CONVERSAR
============================= */
async function abrirConversa() {
  if (conversaUsada.value) {
    $q.notify({ type: 'warning', message: 'Você já conversou com este item.' })
    return
  }

  try {
    const itemId = route.params.id
    const res = await api.get(`/api/questao/item/${itemId}/`) // <-- CORRETO: pega a pergunta

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

function finalizarCaptura() {
  mostrarSucessoRPG.value = false
  router.push({ name: 'mapa' })
}
/* ============================
        RESPONDER QUESTÃO
============================= */
async function responder(letra) {
  try {
    const res = await api.post(`/api/questao/${questao.value.id}/`, {
      resposta: letra
    })

    resultado.value = res.data

    if (res.data.chance !== undefined && res.data.chance !== null) {
      chance.value = res.data.chance
    }

    conversaUsada.value = true // trava o botão conversar

  } catch (err) {
    if (err.response?.data?.error === "Você já conversou com este item.") {
      conversaUsada.value = true
      mostrarDialogo.value = false
      $q.notify({ type: "warning", message: "Você já conversou com este item." })
      return
    }

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

.animacao-bonk,
.animacao-ovo {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 180px;
  z-index: 999;
  pointer-events: none;  /* impede de bloquear cliques */
}

.card-image { position: relative; max-height: 400px; }
.main-img { width: 100%; height: 100%; object-fit: cover; border-radius: 12px; }
.actions-col { display:flex; flex-direction:column; gap:8px; align-items:center; justify-content:center; }
.progress-bar { position:relative; margin-top:12px; height:40px; }
.progress-text { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); font-weight:bold; color:rgb(119, 119, 119); }
.full-width { width:100%; }
</style>
