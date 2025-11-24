<template>
  <q-page class="container q-pa-md">
    <div class="row justify-end q-mb-md">
      <q-btn label="Voltar para o mapa" flat icon="arrow_back" to="/mapa" />
    </div>

    <div v-if="item">
      <div class="card q-pa-md q-mb-xl">
        <div class="row q-col-gutter-lg">
          <div class="col-12 col-md-6">
            <q-img :src="item.imagem" style="width:100%; height:300px" class="rounded-borders" />
          </div>
          <div class="col-12 col-md-6">
            <h1 class="q-mt-none q-mb-sm" style="color:#166534; font-size:36px; font-weight:900; line-height:1.1">
              {{ item.nome }}
            </h1>
            <span class="subtitle-chip q-mb-md">{{ item.tipo }}</span>
            <div class="text-body1 q-mt-md" style="color:#374151; line-height:1.7">
              {{ item.descricao }}
            </div>

            <q-btn
              v-if="item.tipo === 'ANI'"
              color="green-8"
              label="Capturar"
              icon="pets"
              class="q-mt-lg"
              :to="{ name: 'PaginaDeCaptura', params: { id: item.id } }"
            />

            <q-btn
              v-if="item.tipo === 'PLA'"
              color="green-8"
              label="Coletar"
              icon="grass"
              class="q-mt-lg"
              :loading="isColetando"
              @click="coletarPlanta"
            />
            
          </div>
        </div>
      </div>

      <div v-if="item.curiosidades" class="card q-pa-lg q-mb-xl">
        <div class="section-title">
          <q-icon name="emoji_objects" color="amber-8" />
          Curiosidades
        </div>
        <div class="text-body1 q-mb-lg" style="color:#374151; line-height:1.7">
          {{ item.curiosidades }}
        </div>
      </div>
    </div> <div v-else class="text-center q-mt-xl">
      <q-spinner color="primary" size="3em" v-if="isLoading" />
      <div v-else>
        <q-icon name="error_outline" color="red" size="64px" />
        <div class="text-h6 q-mt-md">Item não encontrado</div>
        <q-btn color="primary" label="Voltar para o mapa" class="q-mt-lg" to="/mapa" />
      </div>
    </div>
  </q-page>
</template>


<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router' 
import { api } from 'boot/axios'
import { useQuasar } from 'quasar' 

const route = useRoute()
const router = useRouter() 
const $q = useQuasar()     
const item = ref(null)
const isLoading = ref(true)
const isColetando = ref(false)


onMounted(async () => {
  try {
    const response = await api.get(`/api/item/${route.params.id}/`)
    item.value = response.data
  } catch (err) {
    console.error('Erro ao carregar item:', err)
  } finally {
    isLoading.value = false
  }
})

async function coletarPlanta() {
  if (!item.value) return

  isColetando.value = true
  
  $q.loading.show({ message: `Coletando ${item.value.nome}...` })

  try {
    await api.post('/api/capturas/add-item/', { item_id: item.value.id })
    
    $q.notify({
      type: 'positive',
      color: 'positive',
      icon: 'grass',
      message: `${item.value.nome} foi adicionado(a) à mochila!`,
      position: 'top'
    })

    router.push('/')

  } catch (err) {
    console.error('Erro ao coletar planta:', err)
    const status = err?.response?.status
    
    if (status === 400 || status === 409) {
      $q.notify({ message: `${item.value.nome} já está na mochila.`, color: 'info', position: 'top' });
      router.push('/') 
    
    } else if (status === 401) {
      $q.notify({ message: 'Você precisa estar logado para coletar.', color: 'warning', position: 'top' });
    
    } else {
      $q.notify({ message: 'Erro ao coletar planta. Tente novamente.', color: 'negative', position: 'top' });
    }
  } finally {
    isColetando.value = false
    $q.loading.hide()
  }
}
</script>

<style scoped>
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