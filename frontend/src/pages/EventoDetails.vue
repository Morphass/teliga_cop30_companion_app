<template>
  <q-page class="container q-pa-md">
    <div class="row justify-end q-mb-md">
      <q-btn label="Voltar para o mapa" flat icon="arrow_back" to="/mapa" />
    </div>

    <div v-if="evento">
      <div class="card q-pa-md q-mb-xl">
        <div class="row q-col-gutter-lg">
          <div class="col-12 col-md-6">
            <q-img :src="getImageUrl(evento.imagem)" style="width:100%; height:300px" class="rounded-borders" />
          </div>
          <div class="col-12 col-md-6">
            <h1 class="q-mt-none q-mb-sm" style="color:#166534; font-size:36px; font-weight:900; line-height:1.1">
              {{ evento.titulo }}
            </h1>
            <span class="subtitle-chip q-mb-md">{{ evento.categoria }}</span>
            <div class="text-body1 q-mt-md" style="color:#374151; line-height:1.7">
              {{ evento.descricao }}
            </div>

            <q-btn
              color="green-8"
              icon="backpack"
              label="Guardar na Mochila"
              class="q-mt-lg"
              @click="guardarNaMochila"
            />
          </div>
        </div>
      </div>

      <div class="card q-pa-lg q-mb-xl text-center champion-card">
        <div class="text-h5 text-orange-9 text-weight-bold row justify-center items-center q-mb-md">
          <q-icon name="emoji_events" class="q-mr-sm" color="orange-8" />
          Campeão do Evento
        </div>
        
        <div v-if="evento.nome_campeao" class="q-mt-md animate-fade">
          <q-avatar size="120px" class="shadow-5 q-mb-md" style="border: 4px solid #FFD700">
            <img :src="getImageUrl(evento.imagem_criatura_campeao) || '/icons/animal.png'" style="object-fit: cover; background: white;" />
          </q-avatar>
          <div class="text-h6 text-weight-bold text-dark">{{ evento.nome_campeao }}</div>
          <div class="text-subtitle1 text-grey-8 q-mb-sm">
            Defendendo com: <b>{{ evento.nome_criatura_campeao }}</b>
          </div>
          <q-chip color="red-7" text-color="white" icon="favorite" class="shadow-1">
            {{ evento.vida_criatura_campeao }} HP
          </q-chip>
        </div>

        <div v-else class="q-mt-md text-grey-7 text-body1 q-pa-md bg-grey-2 rounded-borders">
          <q-icon name="flag" size="md" color="grey-5" class="q-mb-sm" />
          <br>
          <strong>Este local está sem proteção!</strong>
          <br>
          Seja o primeiro a dominar este evento.
        </div>

        <q-btn 
          push 
          :color="isChampion ? 'grey-6' : 'red-8'"
          :icon="isChampion ? 'lock' : 'swords'"
          :label="isChampion ? 'Você já domina este local' : 'Desafiar Campeão'"
          :disable="isChampion"
          class="q-mt-lg full-width shadow-3"
          size="lg"
          @click="abrirModalSelecao"
        />
      </div>

      <div v-if="evento.curiosidades" class="card q-pa-lg q-mb-xl">
        <div class="section-title">
          <q-icon name="emoji_objects" color="amber-8" />
          Curiosidades
        </div>
        <div class="text-body1 q-mb-lg" style="color:#374151; line-height:1.7">
          {{ evento.curiosidades }}
        </div>
      </div>

      <div class="card q-pa-lg q-mb-xl">
        <div class="section-title">
          <q-icon name="public" color="green-8" />
          Localização no mapa
        </div>
        <div id="map" class="map q-mb-md" style="height: 300px;"></div>
      </div>
    </div>

    <div v-else class="text-center q-mt-xl">
      <q-spinner color="primary" size="3em" v-if="isLoading" />
      <div v-else>
        <q-icon name="error_outline" color="red" size="64px" />
        <div class="text-h6 q-mt-md">Evento não encontrado</div>
        <q-btn color="primary" label="Voltar para o mapa" class="q-mt-lg" to="/" />
      </div>
    </div>

    <q-dialog v-model="modalBatalha">
      <q-card style="min-width: 350px; max-width: 95vw;">
        <q-card-section class="bg-primary text-white">
          <div class="text-h6 row items-center">
            <q-icon name="swords" class="q-mr-sm" /> Escolha seu Lutador
          </div>
          <div class="text-caption">Selecione uma criatura da sua mochila</div>
        </q-card-section>

        <q-card-section class="q-pa-none scroll" style="max-height: 60vh;">
          <q-list separator v-if="minhaMochila.length > 0">
            <q-item 
              v-for="item in minhaMochila" 
              :key="item.id" 
              clickable 
              v-ripple
              class="q-py-md"
              @click="realizarAtaque(item)"
            >
              <q-item-section avatar>
                <q-avatar rounded size="60px" class="bg-grey-2">
                  <img :src="getImageUrl(item.item.imagem) || '/icons/item_padrao.png'" style="object-fit: cover;">
                </q-avatar>
              </q-item-section>
              
              <q-item-section>
                <q-item-label class="text-weight-bold text-h6 text-green-9">{{ item.item.nome }}</q-item-label>
                <div class="row q-gutter-sm q-mt-xs">
                  <q-badge color="blue-7" class="q-py-xs">
                    <q-icon name="flash_on" size="xs" class="q-mr-xs" /> ATQ: {{ item.ataque }}
                  </q-badge>
                  <q-badge color="red-7" class="q-py-xs">
                    <q-icon name="favorite" size="xs" class="q-mr-xs" /> HP: {{ item.vida_atual }}
                  </q-badge>
                </div>
              </q-item-section>

              <q-item-section side>
                <q-btn round flat icon="play_arrow" color="green-8" size="lg" />
              </q-item-section>
            </q-item>
          </q-list>
          
          <div v-else class="text-center q-pa-xl text-grey-7 column flex-center">
            <q-icon name="pets" size="4em" color="grey-4" class="q-mb-md" />
            <p class="text-h6 text-grey-6">Sua mochila de fauna está vazia!</p>
            <p>Você precisa capturar animais no mapa para poder batalhar.</p>
            <q-btn outline color="primary" label="Ir para o mapa" to="/mapa" v-close-popup class="q-mt-sm" />
          </div>
        </q-card-section>

        <q-card-actions align="right" class="bg-grey-1">
          <q-btn flat label="Cancelar" color="grey-8" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>

  </q-page>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { api } from 'boot/axios'

const route = useRoute()
const router = useRouter()
const $q = useQuasar()
const backendUrl = 'http://127.0.0.1:8000'
const evento = ref(null)
const isLoading = ref(true)
const modalBatalha = ref(false)
const minhaMochila = ref([])
const currentUser = ref(null)

function getImageUrl(imagePath) {
  if (!imagePath) return ''
  return imagePath.startsWith('http') ? imagePath : `${backendUrl}${imagePath}`
}

const isChampion = computed(() => {
  if (!evento.value || !evento.value.nome_campeao || !currentUser.value) return false
  return evento.value.nome_campeao === currentUser.value.username
})
 
async function guardarNaMochila() {
  const token = localStorage.getItem('user_token')
  if (!token) {
    $q.notify({
      type: 'negative',
      message: 'Você precisa fazer login para guardar eventos.',
      icon: 'lock',
      position: 'top',
      actions: [
        { label: 'Entrar', color: 'white', handler: () => router.push('/login') }
      ]
    })
    return
  }

  if (!evento.value || !evento.value.id) {
    $q.notify({ type: 'negative', message: 'Evento inválido.' })
    return
  }

  try {
    await api.post('/api/capturas/eventos/', { evento_id: evento.value.id })
    $q.notify({ type: 'positive', message: `${evento.value.titulo} foi guardado na mochila!` })
  } catch (err) {
    const status = err?.response?.status
    if (status === 400 || status === 409) {
      $q.notify({ type: 'info', message: `${evento.value.titulo} já está na mochila!` })
    } else {
      console.error('Erro ao guardar evento na mochila:', err)
      $q.notify({ type: 'negative', message: 'Erro ao salvar na mochila.' })
    }
  }
}

async function abrirModalSelecao() {
  const token = localStorage.getItem('user_token')
  if (!token) {
    $q.notify({
      type: 'negative',
      message: 'Você precisa estar logado para batalhar.',
      icon: 'lock',
      position: 'top',
      actions: [
        { label: 'Entrar', color: 'white', handler: () => router.push('/login') }
      ]
    })
    return
  }

  try {
    $q.loading.show({ message: 'Preparando para a batalha...' })
    const response = await api.get('/api/capturas/fauna/')
    minhaMochila.value = response.data
    modalBatalha.value = true
  } catch (err) {
    console.error('Erro ao carregar mochila:', err)
    $q.notify({ type: 'negative', message: 'Erro ao buscar dados de batalha.' })
  } finally {
    $q.loading.hide()
  }
}

async function realizarAtaque(meuItem) {
  try {
    modalBatalha.value = false
    $q.loading.show({ 
      message: 'A batalha começou!',
      spinnerColor: 'red',
      backgroundColor: 'black',
      customClass: 'battle-loader'
    })
    
    await new Promise(r => setTimeout(r, 1000))

    const response = await api.post(`/api/events/${evento.value.id}/desafiar/`, {
      mochila_item_id: meuItem.id
    })

    const resultado = response.data
    
    if (resultado.resultado === 'VITORIA') {
      $q.dialog({
        title: '🏆 VITÓRIA!',
        message: `
          <div class="text-center q-pa-sm">
            <div class="text-h5 text-positive text-weight-bold q-mb-md">${resultado.mensagem}</div>
            <div class="text-body1 text-grey-9">${resultado.detalhes || ''}</div>
            <div class="q-mt-md text-caption">Agora você é o Campeão deste local!</div>
          </div>
        `,
        html: true,
        ok: { label: 'Sensacional!', color: 'positive', push: true, size: 'lg' },
        persistent: true
      }).onOk(() => {
        window.location.reload() 
      })
    } else {
      $q.dialog({
        title: '💀 DERROTA',
        message: `
          <div class="text-center q-pa-sm">
            <div class="text-h5 text-negative text-weight-bold q-mb-md">${resultado.mensagem}</div>
            <div class="text-body1 text-grey-9">${resultado.detalhes || ''}</div>
            <div class="q-mt-md text-caption">Tente evoluir suas criaturas ou capturar outras mais fortes!</div>
          </div>
        `,
        html: true,
        ok: { label: 'Entendi', color: 'grey-8', flat: true }
      })
    }

  } catch (err) {
    console.error('Erro na batalha:', err)
    const msg = err.response?.data?.error || 'Erro ao processar o desafio.'
    $q.notify({ type: 'negative', message: msg })
  } finally {
    $q.loading.hide()
  }
}

onMounted(async () => {
  const userData = localStorage.getItem('user_data')
  if (userData && userData !== 'undefined') {
    try {
      currentUser.value = JSON.parse(userData)
    } catch (e) {
      console.error("Erro ao ler user_data:", e)
    }
  }

  try {
    const response = await api.get(`/api/events/${route.params.id}/`)
    evento.value = response.data

    if (evento.value?.latitude != null && evento.value?.longitude != null) {
      await nextTick()
      const mapContainer = document.getElementById('map')
      if (mapContainer) {
        const map = L.map('map').setView([evento.value.latitude, evento.value.longitude], 15)
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '&copy; OpenStreetMap contributors'
        }).addTo(map)

        L.marker([evento.value.latitude, evento.value.longitude])
          .addTo(map)
          .bindPopup(`<b>${evento.value.titulo}</b>`)
      }
    }
  } catch (err) {
    console.error('Erro ao carregar evento:', err)
  } finally {
    isLoading.value = false
  }
})
</script>

<style scoped>
.map {
  width: 100%;
  z-index: 1;
  border-radius: 8px;
}
.subtitle-chip {
  background-color: #e0e0e0;
  color: #333;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 0.85rem;
  display: inline-block;
}
.card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.section-title {
  font-size: 1.25rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  color: #333;
}

.champion-card {
  border: 2px solid #FFD700; 
  background: linear-gradient(to bottom, #fffcf0, #fff);
  position: relative;
  overflow: hidden;
}

.champion-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 6px;
  background: repeating-linear-gradient(
    45deg,
    #FFD700,
    #FFD700 10px,
    #FFA500 10px,
    #FFA500 20px
  );
}

.animate-fade {
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>