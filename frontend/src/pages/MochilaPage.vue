<template>
  <q-page class="q-pa-md flex flex-center">

    <q-card class="mochila-card">

      <div class="q-pa-md row items-center justify-between gt-sm">
        <div class="row items-center">
          <q-icon name="backpack" color="green-8" size="md" />
          <div class="text-h5 text-green-9 text-weight-bold q-ml-md">
            Mochila
          </div>
        </div>
        <q-btn
          flat
          round
          dense
          icon="arrow_back"
          color="primary"
          @click="$router.back()"
        />
      </div>

      <div class="q-pa-md row items-center lt-md">
        <q-btn
          flat
          round
          dense
          icon="arrow_back"
          color="primary"
          @click="$router.back()"
        />
        <q-icon name="backpack" color="red-8" size="md" class="q-ml-sm" />
        <div class="text-h6 text-blue-9 text-weight-bold q-ml-sm">
          Minha Mochila
        </div>
      </div>

      <q-separator />

      <div class="row no-wrap content-container" style="position: relative;">

        <div class="col-3 q-pa-md menu-lateral gt-sm">
          <q-list separator padding class="menu-lista">
            <q-item
              clickable
              v-ripple
              :active="secaoAtiva === 'fauna'"
              @click="secaoAtiva = 'fauna'"
              active-class="menu-item-ativo"
            >
              <q-item-section avatar><q-icon name="pets" /></q-item-section>
              <q-item-section>Fauna</q-item-section>
            </q-item>

            <q-item
              clickable
              v-ripple
              :active="secaoAtiva === 'flora'"
              @click="secaoAtiva = 'flora'"
              active-class="menu-item-ativo"
            >
              <q-item-section avatar><q-icon name="grass" /></q-item-section>
              <q-item-section>Flora</q-item-section>
            </q-item>

            <q-item
              clickable
              v-ripple
              :active="secaoAtiva === 'itens'"
              @click="secaoAtiva = 'itens'"
              active-class="menu-item-ativo"
            >
              <q-item-section avatar><q-icon name="inventory_2" /></q-item-section>
              <q-item-section>Itens</q-item-section>
            </q-item>

            <q-item
              clickable
              v-ripple
              :active="secaoAtiva === 'pocoes'"
              @click="secaoAtiva = 'pocoes'"
              active-class="menu-item-ativo"
            >
              <q-item-section avatar><q-icon name="science" /></q-item-section>
              <q-item-section>Poções</q-item-section>
            </q-item>

            <q-item
              clickable
              v-ripple
              :active="secaoAtiva === 'eventos'"
              @click="secaoAtiva = 'eventos'"
              active-class="menu-item-ativo"
            >
              <q-item-section avatar><q-icon name="event" /></q-item-section>
              <q-item-section>Eventos</q-item-section>
            </q-item>
          </q-list>
        </div>

        <div class="mobile-floating-nav lt-md">
          <q-avatar
            icon="backpack"
            color="orange-5"
            text-color="white"
            size="lg"
            class="q-mb-sm floating-backpack"
          />

          <q-btn
            :unelevated="secaoAtiva !== 'fauna'"
            :color="secaoAtiva === 'fauna' ? 'blue-6' : 'blue-3'"
            icon="pets"
            @click="secaoAtiva = 'fauna'"
            class="nav-tab"
            :class="{ 'nav-tab-active': secaoAtiva === 'fauna' }"
          />
          <q-btn
            :unelevated="secaoAtiva !== 'flora'"
            :color="secaoAtiva === 'flora' ? 'green-6' : 'green-3'"
            icon="grass"
            @click="secaoAtiva = 'flora'"
            class="nav-tab"
            :class="{ 'nav-tab-active': secaoAtiva === 'flora' }"
          />
          <q-btn
            :unelevated="secaoAtiva !== 'itens'"
            :color="secaoAtiva === 'itens' ? 'orange-6' : 'orange-3'"
            icon="folder"
            @click="secaoAtiva = 'itens'"
            class="nav-tab"
            :class="{ 'nav-tab-active': secaoAtiva === 'itens' }"
          />
          <q-btn
            :unelevated="secaoAtiva !== 'pocoes'"
            :color="secaoAtiva === 'pocoes' ? 'red-6' : 'red-3'"
            icon="science"
            @click="secaoAtiva = 'pocoes'"
            class="nav-tab"
            :class="{ 'nav-tab-active': secaoAtiva === 'pocoes' }"
          />
          <q-btn
            :unelevated="secaoAtiva !== 'eventos'"
            :color="secaoAtiva === 'eventos' ? 'deep-purple-6' : 'deep-purple-3'"
            icon="event"
            @click="secaoAtiva = 'eventos'"
            class="nav-tab"
            :class="{ 'nav-tab-active': secaoAtiva === 'eventos' }"
          />
        </div>

        <div class="col q-pa-md scroll-area">

          <div class="text-caption text-grey-7 q-mb-md lt-md">
            Aqui ficam os itens, poções e eventos que você capturou.
          </div>

          <div v-if="secaoAtiva === 'fauna'">
            <div class="row items-center q-mb-md">
              <q-icon name="pets" color="blue-6" size="sm" class="lt-md q-mr-sm" />
              <div class="text-h6">Fauna</div>
            </div>
            <div v-if="fauna.length === 0" class="text-grey-7 text-italic text-center q-mt-md">
              Você ainda não capturou nenhuma fauna.
            </div>
            <div class="item-grid">
              <q-card
                v-for="captura in fauna"
                :key="captura.id"
                flat
                bordered
                class="item-card"
                @click="abrirModalDetalhe(captura.item, 'fauna', captura.foi_captura_forcada, captura.id, captura.captured_at)"
              >
                <q-img :src="captura.item.imagem || 'https://i.imgur.com/qL4lF3c.png'" :ratio="1">
                  <div class="absolute-bottom text-subtitle2 text-center">
                    {{ captura.item.nome }}
                  </div>
                </q-img>
              </q-card>
            </div>
          </div>

          <div v-if="secaoAtiva === 'flora'">
            <div class="row items-center q-mb-md">
              <q-icon name="grass" color="green-6" size="sm" class="lt-md q-mr-sm" />
              <div class="text-h6">Flora</div>
            </div>
            <div v-if="flora.length === 0" class="text-grey-7 text-italic text-center q-mt-md">
              Você ainda não capturou nenhuma flora.
            </div>
            <div class="item-grid">
              <q-card
                v-for="captura in flora"
                :key="captura.id"
                flat
                bordered
                class="item-card"
                @click="abrirModalDetalhe(captura.item, 'flora', captura.foi_captura_forcada, captura.id, captura.captured_at)"
              >
                <q-img :src="captura.item.imagem || 'https://i.imgur.com/qL4lF3c.png'" :ratio="1">
                  <div class="absolute-bottom text-subtitle2 text-center">
                    {{ captura.item.nome }}
                  </div>
                </q-img>
              </q-card>
            </div>
          </div>

          <div v-if="secaoAtiva === 'itens'">
            <div class="row items-center q-mb-md">
              <q-icon name="folder" color="orange-6" size="sm" class="lt-md q-mr-sm" />
              <div class="text-h6">Itens</div>
            </div>
            <div v-if="itens.length === 0" class="text-grey-7 text-italic text-center q-mt-md">
              Você ainda não capturou nenhum item.
            </div>
            <div class="item-grid">
              <q-card
                v-for="captura in itens"
                :key="captura.id"
                flat
                bordered
                class="item-card"
                @click="abrirModalDetalhe(captura.item, 'item', false, captura.id, captura.captured_at)"
              >
                <q-img :src="captura.item.imagem || 'https://i.imgur.com/qL4lF3c.png'" :ratio="1">
                  <div class="absolute-bottom text-subtitle2 text-center">
                    {{ captura.item.nome }}
                  </div>
                </q-img>
              </q-card>
            </div>
          </div>

          <div v-if="secaoAtiva === 'pocoes'">
            <div class="row items-center q-mb-md">
              <q-icon name="science" color="red-6" size="sm" class="lt-md q-mr-sm" />
              <div class="text-h6">Poções</div>
            </div>
            <div v-if="pocoes.length === 0" class="text-grey-7 text-italic text-center q-mt-md">
              Você ainda não capturou nenhuma poção.
            </div>
            <div class="item-grid">
              <q-card
                v-for="captura in pocoes"
                :key="captura.id"
                flat
                bordered
                class="item-card"
                @click="abrirModalDetalhe(captura.item, 'pocao', false, captura.id, captura.captured_at)"
              >
                <q-img :src="captura.item.imagem || 'https://i.imgur.com/qL4lF3c.png'" :ratio="1">
                  <div class="absolute-bottom text-subtitle2 text-center">
                    {{ captura.item.nome }}
                  </div>
                </q-img>
              </q-card>
            </div>
          </div>

          <div v-if="secaoAtiva === 'eventos'">
            <div class="row items-center q-mb-md">
              <q-icon name="event" color="deep-purple-6" size="sm" class="lt-md q-mr-sm" />
              <div class="text-h6">Eventos</div>
            </div>
            <div v-if="eventos.length === 0" class="text-grey-7 text-italic text-center q-mt-md">
              Você ainda não participou de nenhum evento.
            </div>
            <div class="item-grid">
              <q-card
                v-for="captura in eventos"
                :key="captura.id"
                flat
                bordered
                class="item-card"
                @click="abrirModalDetalhe(captura.evento, 'evento', false, captura.id, captura.captured_at)"
              >
                <q-img :src="captura.evento.imagem || 'https://i.imgur.com/qL4lF3c.png'" :ratio="1">
                  <div class="absolute-bottom text-subtitle2 text-center">
                    {{ captura.evento.titulo }}
                  </div>
                </q-img>
              </q-card>
            </div>
          </div>

        </div>
      </div>

    </q-card>

    <q-dialog v-model="modalDetalheAberto">
      <q-card style="width: 400px; max-width: 90vw;">
        <q-img :src="itemSelecionado?.imagem || 'https://i.imgur.com/qL4lF3c.png'" :ratio="16/9" />
        <q-card-section>
          <div class="text-h5 text-weight-bold">{{ itemSelecionado?.nome || itemSelecionado?.titulo }}</div>
          <div class="text-caption text-grey text-capitalize">{{ tipoItemSelecionado }}</div>
        </q-card-section>
        <q-card-section class="q-pt-none">
          <p>{{ itemSelecionado?.descricao || itemSelecionado?.categoria }}</p>
          <div v-if="tipoItemSelecionado === 'pocao' && itemSelecionado?.bonus_captura">
            <q-icon name="arrow_upward" color="positive" /> Bônus de Captura: +{{ itemSelecionado.bonus_captura }}%
          </div>
          <div v-if="tipoItemSelecionado === 'fauna' && foiForcada" class="q-mt-md text-negative">
            <q-icon name="warning" /> <span>Capturado à força</span>
          </div>
          <div v-if="tipoItemSelecionado === 'fauna' && !foiForcada" class="q-mt-md text-positive">
            <q-icon name="check_circle" /> <span>Capturado em harmonia</span>
          </div>
          <div v-if="tipoItemSelecionado === 'fauna' && dataCapturaSelecionada" class="q-mt-md text-grey-8">
            <q-icon name="calendar_month" class="q-mr-xs" /> Capturado em: {{ formatarData(dataCapturaSelecionada) }}
          </div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Fechar" color="primary" v-close-popup />
          <q-btn
            v-if="tipoItemSelecionado === 'evento'"
            flat
            label="Remover"
            color="negative"
            @click="confirmarRemocao"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="dialogRemocaoAberto" persistent>
      <q-card>
        <q-card-section class="row items-center">
          <q-icon name="warning" color="warning" size="md" class="q-mr-sm" />
          <div class="text-h6">Remover evento</div>
        </q-card-section>
        <q-card-section>
          Tem certeza que deseja remover o evento
          <b>{{ itemSelecionado?.titulo }}</b> da mochila?
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="grey" v-close-popup />
          <q-btn flat label="Remover" color="negative" @click="removerEventoConfirmado" />
        </q-card-actions>
      </q-card>
    </q-dialog>

  </q-page>
</template>

<script>
import { defineComponent, ref, onMounted } from "vue";
import { useQuasar } from "quasar";
import { api } from "boot/axios";

export default defineComponent({
  name: 'MochilaPage',
  
  setup() {
    const $q = useQuasar();
    const secaoAtiva = ref("fauna");

    const fauna = ref([]);
    const flora = ref([]);
    const itens = ref([]);
    const pocoes = ref([]);
    const eventos = ref([]);

    const modalDetalheAberto = ref(false);
    const dialogRemocaoAberto = ref(false);
    const itemSelecionado = ref(null);
    const tipoItemSelecionado = ref("");
    const foiForcada = ref(false);
    const idCapturaSelecionada = ref(null);
    const dataCapturaSelecionada = ref(null);

    onMounted(async () => {
      try {
        const [resFauna, resFlora, resItens, resPocoes, resEventos] = await Promise.all([
          api.get("/api/capturas/fauna/"),
          api.get("/api/capturas/flora/"),
          api.get("/api/capturas/itens/"),
          api.get("/api/capturas/pocoes/"),
          api.get("/api/capturas/eventos/"),
        ]);
        fauna.value = resFauna.data;
        flora.value = resFlora.data;
        itens.value = resItens.data;
        pocoes.value = resPocoes.data;
        eventos.value = resEventos.data;
      } catch (err) {
        console.error(err);
        $q.notify({ type: "negative", message: "Erro ao carregar mochila" });
      }
    });

    function abrirModalDetalhe(item, tipo, capturaForcada, idCaptura, dataCaptura) {
      itemSelecionado.value = item;
      tipoItemSelecionado.value = tipo;
      foiForcada.value = capturaForcada;
      idCapturaSelecionada.value = idCaptura;
      dataCapturaSelecionada.value = dataCaptura;
      modalDetalheAberto.value = true;
    }

    function confirmarRemocao() {
      modalDetalheAberto.value = false;
      dialogRemocaoAberto.value = true;
    }

    async function removerEventoConfirmado() {
      if (!idCapturaSelecionada.value) return;
      try {
        await api.delete(`/api/capturas/eventos/${idCapturaSelecionada.value}/`);
        eventos.value = eventos.value.filter((e) => e.id !== idCapturaSelecionada.value);
        $q.notify({ type: "positive", message: "Evento removido com sucesso!" });
      } catch (error) {
        console.error("Erro ao remover evento:", error);
        $q.notify({ type: "negative", message: "Não foi possível remover o evento." });
      } finally {
        dialogRemocaoAberto.value = false;
      }
    }

    function formatarData(dataISO) {
      if (!dataISO) return "";
      return new Date(dataISO).toLocaleString("pt-BR", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
      });
    }

    return {
      secaoAtiva,
      fauna,
      flora,
      itens,
      pocoes,
      eventos,
      modalDetalheAberto,
      dialogRemocaoAberto,
      itemSelecionado,
      tipoItemSelecionado,
      foiForcada,
      idCapturaSelecionada,
      dataCapturaSelecionada,
      abrirModalDetalhe,
      confirmarRemocao,
      removerEventoConfirmado,
      formatarData,
    };
  },
});
</script>

<style scoped>
.mochila-card {
  max-width: 1100px;
  width: 100%;
  height: 80vh;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.menu-lateral {
  background-color: #f9f9f9;
  border-right: 1px solid #eee;
}

.menu-lista .q-item {
  border-radius: 8px;
  margin-bottom: 4px;
  color: #555;
  font-weight: 500;
}

.menu-lista .menu-item-ativo {
  background-color: #e6f6e6;
  color: #2e7d32;
  font-weight: 700;
}

.item-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 16px;
}

.item-card {
  cursor: pointer;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}

.item-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.12);
}

.mobile-floating-nav {
  position: absolute;
  top: 24px;
  right: 0px;
  display: flex;
  flex-direction: column;
  z-index: 10;
  align-items: flex-end;
}

.floating-backpack {
  margin-left: -12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  margin-right: -4px;
  border: 2px solid white;
}

.nav-tab {
  width: 48px;
  height: 36px;
  border-radius: 8px 0 0 8px;
  margin-bottom: 8px;
  transition: all 0.2s ease;
  margin-right: -10px;
  box-shadow: -2px 2px 5px rgba(0,0,0,0.1);
  border: 1px solid rgba(0,0,0,0.05);
  padding: 0;
}

.nav-tab-active {
  margin-right: 0px;
  width: 52px;
}

@media (max-width: 768px) {
  .mochila-card {
    height: auto;
    min-height: 85vh;
  }
  .content-container {
    flex-direction: column;
  }
  .item-grid {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  }
  .scroll-area {
    padding-right: 40px; 
  }
}
</style>