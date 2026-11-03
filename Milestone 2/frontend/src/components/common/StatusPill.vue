<script setup>
import { computed } from 'vue';
const props = defineProps({ value: { type: String, required: true } });
const cls = computed(() => props.value.replace(/[^a-z]/g, ''));
</script>

<template>
  <span class="pill" :class="cls">{{ value }}</span>
</template>
