<script setup>
defineProps({ count: { type: Number, required: true }, label: String, to: String, cta: String });
</script>

<template>
  <div class="stat alert" :class="{ zero: !count }">
    <div class="metric">{{ count }}</div>
    <div class="lbl">{{ label }}</div>
    <router-link v-if="count && to" :to="to">{{ cta }}</router-link>
  </div>
</template>
