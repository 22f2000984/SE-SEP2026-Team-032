<script setup>
import AppHeader from '../components/common/AppHeader.vue';
import { API_ON } from '../services/api';
</script>

<template>
  <AppHeader />
  <main class="page"><slot /></main>
  <footer class="page-footer">Team 032 – Himalayan Coders · {{ API_ON ? 'Connected to the Mentor Connect backend' : 'Milestone 2 frontend prototype (sample data, no backend)' }}</footer>
</template>
