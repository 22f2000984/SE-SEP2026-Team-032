<script setup>
defineProps({ total: { type: Number, required: true } });
</script>

<template>
  <span><span class="scorebar"><span :style="{ width: total + '%' }"></span></span> <b>{{ total }}</b>/100</span>
</template>
