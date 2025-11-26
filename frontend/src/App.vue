<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue'
import { Platform } from 'quasar'
import { StatusBar } from '@capacitor/status-bar'

defineOptions({
  name: 'App'
})

onMounted(async () => {
  if (Platform.is.capacitor) {
    try {
      await StatusBar.hide()
    } catch (e) {
      console.warn('Erro ao ocultar Status Bar (Plugin instalado?):', e)
    }
  }
})
</script>