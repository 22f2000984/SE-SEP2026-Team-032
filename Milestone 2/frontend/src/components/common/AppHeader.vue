<script setup>
import { computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { NAV, HOME } from '../../config/constants';
import { session, logout } from '../../services/auth';
import BrandLogo from './BrandLogo.vue';

const router = useRouter();
const route = useRoute();
const links = computed(() => (session.value ? NAV[session.value.role] : []));
const home = computed(() => (session.value ? HOME[session.value.role] : '/login'));
const who = computed(() => (session.value.role === 'admin' ? session.value.name : `${session.value.name} (${session.value.role})`));

/* The first link of each role (the dashboard) is active only on its own page; the others also cover their sub-pages. */
function isActive(l) {
  return l.exact ? route.path === l.to : route.path === l.to || route.path.startsWith(l.to + '/');
}

function signOut() {
  logout();
  router.push('/login');
}
</script>

<template>
  <header class="app-header">
    <router-link class="brand" :to="home"><BrandLogo /> Mentor Connect</router-link>
    <nav class="nav" aria-label="Main">
      <router-link v-for="l in links" :key="l.to" :to="l.to" active-class="" exact-active-class="" :class="{ active: isActive(l) }">{{ l.label }}</router-link>
      <span v-if="session" class="who">{{ who }}</span>
      <button class="link" type="button" @click="signOut">Log out</button>
    </nav>
  </header>
</template>
