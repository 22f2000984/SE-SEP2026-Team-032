<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import AppLayout from './layouts/AppLayout.vue';
import AuthLayout from './layouts/AuthLayout.vue';
import ToastHost from './components/common/ToastHost.vue';

const route = useRoute();
const layout = computed(() => (route.meta.layout === 'auth' ? AuthLayout : AppLayout));
</script>

<template>
  <component :is="layout">
    <router-view />
  </component>
  <ToastHost />
</template>
