<script setup>
import { TOPICS } from '../../config/constants';

/* Tick boxes for the shared topic list. Use with v-model. */
const model = defineModel({ type: Array, default: () => [] });
</script>

<template>
  <div class="checks">
    <label v-for="t in TOPICS" :key="t"><input v-model="model" type="checkbox" :value="t" /> {{ t }}</label>
  </div>
</template>
