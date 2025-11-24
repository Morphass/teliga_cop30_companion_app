<template>
  <q-page class="q-pa-md green-bg map-page-container">
    <div class="q-pa-md flex flex-center">
      <q-card class="main-card">
        <q-card-section class="banner text-center">
          <h1>Te Liga!</h1>
          <p>Bem-vindo(a) ao mapa de eventos!</p>
        </q-card-section>

        <q-card-section>
          <div class="relative-position">

            <q-no-ssr>
              <l-map
                v-if="isMounted"
                ref="mapRef"
                style="height: 70vh; width: 100%; border-radius: 1rem; overflow: hidden; position: relative;"
                :zoom="13"
                :center="mapCenter"
              >
                <l-tile-layer
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                />

                <l-marker
                  v-if="usuarioPos"
                  :lat-lng="usuarioPos"
                  :icon="usuarioIcon"
                >
                  <l-popup>Você está aqui</l-popup>
                </l-marker>

                <l-marker
                  v-for="evento in eventosFixosValidos"
                  :key="`evento-${evento.id}`"
                  :lat-lng="[evento.latitude, evento.longitude]"
                  @click="irParaDetalhesEvento(evento.id)"
                >
                  <l-popup>{{ evento.titulo }}</l-popup>
                </l-marker>

                <l-marker
                  v-for="item in itensAleatoriosValidos"
                  :key="`item-${item.id}-${item.latitude}`"
                  :lat-lng="[item.latitude, item.longitude]"
                  :icon="getIcon(item.tipo)"
                  @click="handleItemClick(item)"
                >
                  <l-popup>
                    <b>{{ item.nome }}</b>
                    <div v-if="item.tipo === 'POC'">
                      Bônus de Captura: +{{ item.bonus_captura }}%
                      <br /><small>Clique no item para coletar</small>
                    </div>
                    <div v-if="item.tipo === 'ANI' || item.tipo === 'PLA'">
                      <br /><small>Clique no item para ver detalhes</small>
                    </div>
                  </l-popup>
                </l-marker>
              </l-map>
            </q-no-ssr>

            <q-btn 
              square
              size="lg"
              icon="event"
              color="green-8"
              @click="eventosDrawerAberto = true"
              class="botao-eventos"
            >
              <q-tooltip>Meus Eventos</q-tooltip>
              <q-badge 
                v-if="meusEventos.length > 0" 
                color="red" 
                floating
              >
                {{ meusEventos.length }}
              </q-badge>
            </q-btn>
            </div>
        </q-card-section>
      </q-card>
    </div>

    <q-dialog
      v-model="eventosDrawerAberto"
      position="right"
    >
      <q-card style="height: 100%; width: 350px; max-width: 90vw; display: flex; flex-direction: column;">
        <q-scroll-area class="fit q-pa-md">
          <div class="row items-center justify-between q-mb-md">
            <div class="text-h6">Meus Eventos Salvos</div>
            <q-btn 
              flat 
              round 
              dense 
              icon="close" 
              @click="eventosDrawerAberto = false" 
            />
          </div>
          
          <div v-if="meusEventos.length === 0" class="q-pa-md text-grey-7">
            Você ainda não salvou nenhum evento.
          </div>

          <q-card 
            v-for="captura in meusEventos" 
            :key="captura.id"
            class="q-mb-md"
            flat 
            bordered
          >
            <q-card-section>
              <div class="row items-center justify-between no-wrap">
                <div class="text-h6 col-shrink" style="overflow-wrap: break-word;">
                  {{ captura.evento.titulo }}
                </div>
                <q-badge
                  :color="getStatusEvento(captura.evento.data).color"
                  :label="getStatusEvento(captura.evento.data).text"
                  class="q-ml-md"
                />
              </div>
            </q-card-section>
            
            <q-card-section class="q-pt-none text-grey-8">
              <div class="row items-center">
                <q-icon name="calendar_month" class="q-mr-sm" />
                <span>{{ formatarData(captura.evento.data) }}</span>
              </div>
            </q-card-section>

            <q-separator />

            <q-card-actions align="right">
              <q-btn 
                flat 
                color="primary" 
                label="Ver Detalhes" 
                @click="irParaDetalhesEvento(captura.evento.id)"
              />
            </q-card-actions>
          </q-card>
          
        </q-scroll-area>
      </q-card>
    </q-dialog>

  </q-page>
</template>

<script setup>
defineOptions({ name: 'MapaPage' })
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { LMap, LTileLayer, LMarker, LPopup } from '@vue-leaflet/vue-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { api } from 'boot/axios'
import { useQuasar } from 'quasar'
import { Geolocation } from '@capacitor/geolocation'
import iconUrl from 'leaflet/dist/images/marker-icon.png'
import shadowUrl from 'leaflet/dist/images/marker-shadow.png'
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png'
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({ iconRetinaUrl, iconUrl, shadowUrl })

const router = useRouter()
const $q = useQuasar()
const isMounted = ref(false)
const mapRef = ref(null)
const mapCenter = ref([-1.4558, -48.4902]) 
const usuarioPos = ref(null)
const eventosFixos = ref([])
const itensAleatorios = ref([])
const eventosDrawerAberto = ref(false)
const meusEventos = ref([])
const usuarioIcon = L.icon({
  iconUrl: '/icons/usuario.png',
  iconSize: [40, 40],
  iconAnchor: [20, 40]
})

const eventosFixosValidos = computed(() => eventosFixos.value.filter(e => e.latitude != null && e.longitude != null))
const itensAleatoriosValidos = computed(() => itensAleatorios.value.filter(i => i.latitude != null && i.longitude != null))

function getIcon(tipo) {
  const largura = 40;
  const altura = 40;
  const anchor = [largura / 2, altura];
  let url = '/icons/item_padrao.png';
  if (tipo === 'ANI') url = '/icons/animal.png';
  if (tipo === 'PLA') url = '/icons/planta.png';
  if (tipo === 'POC') url = '/icons/potion.svg';
  return L.icon({ iconUrl: url, iconSize: [largura, altura], iconAnchor: anchor });
}

function irParaDetalhesEvento(id) {
  eventosDrawerAberto.value = false
  router.push(`/details/${id}`)
}

async function coletarPocao(pocao) {
  if (!pocao || !pocao.id) {
    $q.notify({ message: 'Poção inválida.', color: 'negative', position: 'top' })
    return
  }
  try {
    await api.post('/api/capturas/pocoes/', { pocao_id: pocao.id })
    itensAleatorios.value = itensAleatorios.value.filter(
      (item) => !(item.id === pocao.id && item.latitude === pocao.latitude)
    );
    $q.notify({
      message: `${pocao.nome} coletada e guardada na mochila!`,
      color: 'positive',
      icon: 'check_circle',
      position: 'top'
    });
  } catch (err) {
    const status = err?.response?.status
    if (status === 400 || status === 409) {
      $q.notify({
        message: `${pocao.nome} já foi coletada.`,
        color: 'info',
        icon: 'info',
        position: 'top'
      });
    } else if (status === 401) {
      $q.notify({
        message: 'Você precisa estar logado para coletar poções.',
        color: 'warning',
        position: 'top'
      });
    } else {
      console.error('Erro ao coletar poção:', err)
      $q.notify({
        message: 'Erro ao coletar poção. Tente novamente.',
        color: 'negative',
        position: 'top'
      });
    }
  }
}

function handleItemClick(item) {
  if (item.tipo === 'POC') coletarPocao(item);
  else router.push(`/item/${item.id}?lat=${item.latitude}&lon=${item.longitude}`);
}

async function obterPosicaoUsuario() {
  try {
    const permission = await Geolocation.checkPermissions();
    if (permission.location !== 'granted') {
      const request = await Geolocation.requestPermissions();
      if (request.location !== 'granted') {
        $q.notify({
          message: 'A permissão de localização é essencial para o mapa.',
          color: 'negative',
          icon: 'location_off'
        });
        return; 
      }
    }

    const position = await Geolocation.getCurrentPosition({
      enableHighAccuracy: true, 
      timeout: 10000 
    });

    usuarioPos.value = [position.coords.latitude, position.coords.longitude]
    mapCenter.value = usuarioPos.value
    
    if (mapRef.value?.mapObject) {
      mapRef.value.mapObject.setView(usuarioPos.value, 13);
    }

    await carregarItensProximos()

  } catch (err) {
    console.error('Erro ao obter localização nativa:', err);
    $q.notify({
      message: 'Não foi possível obter sua localização. Verifique se o GPS está ativado.',
      color: 'negative',
      icon: 'error'
    });
  }
}

async function carregarItensProximos() {
  if (!usuarioPos.value) return;
  try {
    const response = await api.post('/api/itens_proximos/', {
      latitude: usuarioPos.value[0],
      longitude: usuarioPos.value[1],
      qtd_itens: 10
    })
    itensAleatorios.value = response.data;
  } catch (err) {
    console.error('Erro ao carregar itens próximos:', err)
  }
}

async function carregarEventosFixos() {
  try {
    const response = await api.get('/api/events/')
    eventosFixos.value = response.data
  } catch (err) {
    console.error('Erro ao carregar eventos fixos:', err)
  }
}

async function carregarMeusEventos() {
  try {
    const response = await api.get('/api/capturas/eventos/')
    meusEventos.value = response.data
  } catch (err) {
    console.error('Erro ao carregar meus eventos:', err)
  }
}

function formatarData(dataISO) {
  if (!dataISO) return '';
  const data = new Date(dataISO);
  return data.toLocaleDateString('pt-BR', {
    timeZone: 'UTC', 
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  });
}

function getStatusEvento(dataISO) {
  if (!dataISO) return { text: 'Sem data', color: 'grey' };
  const hoje = new Date();
  hoje.setHours(0, 0, 0, 0); 
  const dataEv = new Date(dataISO + 'T00:00:00Z'); 
  
  if (dataEv < hoje) {
    return { text: 'Já passou', color: 'grey-7' };
  } else {
    return { text: 'Próximo', color: 'positive' };
  }
}

onMounted(async () => {
  isMounted.value = true
  obterPosicaoUsuario() 
  await carregarEventosFixos();
  await carregarMeusEventos();
})
</script>

<style scoped>
.main-card {
  width: 100%;
  max-width: 1000px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.banner {
  background: linear-gradient(90deg, #2e7d32, #43a047);
  color: white;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.25);
  padding: 2rem 1rem;
  border-bottom: 4px solid #66bb6a;
}

.banner h1 {
  font-size: 2.2rem;
  font-weight: 700;
  margin-bottom: 0.4rem;
  letter-spacing: 1px;
}

.banner p {
  font-size: 1.2rem;
  opacity: 0.95;
  margin: 0;
}

.botao-eventos {
  position: absolute;
  top: 50%;
  right: 10px;
  transform: translateY(-50%);
  z-index: 1000;
  width: 50px;
  height: 50px;
  border-radius: 10px; 
  box-shadow: 0 3px 8px rgba(0,0,0,0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.leaflet-popup-content-wrapper {
  background: white;
  color: #333;
  font-size: 0.95rem;
  border-radius: 10px;
}

.leaflet-popup-tip {
  background: white;
}

b {
  color: #2e7d32;
  font-weight: 600;
}
small {
  color: #777;
  font-size: 0.8rem;
}
</style>