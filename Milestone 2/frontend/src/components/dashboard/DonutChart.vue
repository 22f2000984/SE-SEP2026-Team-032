<script setup>
import { computed } from 'vue';

/* A ring split into coloured parts. Pure SVG, no chart library. */
const props = defineProps({ parts: { type: Array, required: true }, centre: [String, Number], caption: String });
const R = 52, C = 2 * Math.PI * R;
const total = computed(() => props.parts.reduce((s, p) => s + p.value, 0));
const arcs = computed(() => {
  let offset = 0;
  return props.parts.filter(p => p.value > 0).map(p => {
    const len = (p.value / total.value) * C;
    const arc = { color: p.color, dash: `${len} ${C - len}`, offset: -offset };
    offset += len;
    return arc;
  });
});
</script>

<template>
  <svg class="donut" viewBox="0 0 140 140" role="img" :aria-label="caption">
    <circle cx="70" cy="70" :r="R" fill="none" stroke="#efe7f6" stroke-width="18" />
    <circle v-for="(a, i) in arcs" :key="i" cx="70" cy="70" :r="R" fill="none" :stroke="a.color" stroke-width="18"
      :stroke-dasharray="a.dash" :stroke-dashoffset="a.offset" transform="rotate(-90 70 70)" />
    <text x="70" y="72" text-anchor="middle" class="donut-num">{{ centre }}</text>
    <text x="70" y="92" text-anchor="middle" class="donut-cap">{{ caption }}</text>
  </svg>
</template>
