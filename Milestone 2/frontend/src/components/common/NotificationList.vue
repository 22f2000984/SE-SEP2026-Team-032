<script setup>
import { when } from '../../utils/format';
defineProps({ items: { type: Array, required: true }, empty: { type: String, default: 'No notifications yet.' } });
</script>

<template>
  <ul class="list">
    <li v-for="n in items" :key="n.id"><span v-if="n.email" class="pill email">email</span> {{ n.text }} <span class="muted">· {{ when(n.at) }}</span></li>
    <li v-if="!items.length" class="muted">{{ empty }}</li>
  </ul>
</template>
