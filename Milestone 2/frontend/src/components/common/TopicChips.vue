<script setup>
defineProps({ topics: { type: Array, default: () => [] } });
</script>

<template>
  <span v-if="topics.length"><span v-for="t in topics" :key="t" class="chip">{{ t }}</span></span>
  <span v-else>-</span>
</template>
