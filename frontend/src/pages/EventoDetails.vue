<template>
  <q-page class="container q-pa-md">
    <!-- Botão de voltar -->
    <div class="row justify-end q-mb-md">
      <q-btn label="Voltar para o mapa" flat icon="arrow_back" to="/mapa" />
    </div>

    <!-- Detalhes do evento -->
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

            <!-- Botão para guardar na mochila -->
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

      <!-- Curiosidades -->
      <div v-if="evento.curiosidades" class="card q-pa-lg q-mb-xl">
        <div class="section-title">
          <q-icon name="emoji_objects" color="amber-8" />
          Curiosidades
        </div>
        <div class="text-body1 q-mb-lg" style="color:#374151; line-height:1.7">
          {{ evento.curiosidades }}
        </div>
      </div>

      <!-- Localização no mapa -->
      <div class="card q-pa-lg q-mb-xl">
        <div class="section-title">
          <q-icon name="public" color="green-8" />
          Localização no mapa
        </div>
        <div id="map" class="map q-mb-md" style="height: 300px;"></div>
      </div>
    </div>

    <!-- Caso evento não encontrado -->
    <div v-else class="text-center q-mt-xl">
      <q-spinner color="primary" size="3em" v-if="isLoading" />
      <div v-else>
        <q-icon name="error_outline" color="red" size="64px" />
        <div class="text-h6 q-mt-md">Evento não encontrado</div>
        <q-btn color="primary" label="Voltar para o mapa" class="q-mt-lg" to="/" />
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useQuasar } from 'quasar'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { api } from 'boot/axios'

const route = useRoute()
const evento = ref(null)
const isLoading = ref(true)
const $q = useQuasar()
const backendUrl = 'http://127.0.0.1:8000'
function getImageUrl(imagePath) {
  if (!imagePath) return ''
  return imagePath.startsWith('http') ? imagePath : `${backendUrl}${imagePath}`
}
 
async function guardarNaMochila() {
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

onMounted(async () => {
  try {
    const response = await api.get(`/api/events/${route.params.id}/`)
    evento.value = response.data

    if (evento.value?.latitude != null && evento.value?.longitude != null) {
      await nextTick()

      const map = L.map('map').setView([evento.value.latitude, evento.value.longitude], 15)
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
      }).addTo(map)

      L.marker([evento.value.latitude, evento.value.longitude])
        .addTo(map)
        .bindPopup(`<b>${evento.value.titulo}</b>`)
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
</style>
