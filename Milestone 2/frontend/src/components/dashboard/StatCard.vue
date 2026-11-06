<script setup>
defineProps({ label: String, value: [String, Number], unit: String, sub: String, tone: { type: String, default: 'violet' }, to: String });
</script>

<template>
  <component :is="to ? 'router-link' : 'div'" :to="to" class="stat" :class="[tone, { link: to }]">
    <span class="stat-label">{{ label }}</span>
    <span class="stat-value">{{ value }}<small v-if="unit">{{ unit }}</small></span>
    <span class="stat-sub">{{ sub }}</span>
  </component>
</template>
