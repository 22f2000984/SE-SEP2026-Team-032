<script setup>
defineProps({ eyebrow: String, title: String, intro: String });
</script>

<template>
  <div>
    <div class="eyebrow">{{ eyebrow }}</div>
    <h1>{{ title }}<slot name="badge" /></h1>
    <p v-if="intro" class="muted">{{ intro }}</p>
  </div>
</template>
