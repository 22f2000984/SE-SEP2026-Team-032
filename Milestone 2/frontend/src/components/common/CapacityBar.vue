<script setup>
import { computed } from 'vue';
import { useDb } from '../../composables/useDb';
import { used, maxOf } from '../../services/matching';

const props = defineProps({ mentorId: { type: Number, required: true } });
const { db } = useDb();
const taken = computed(() => used(db, props.mentorId));
const max = computed(() => maxOf(db, props.mentorId));
</script>

<template>
  <span>
    <span class="scorebar cap" :class="{ full: taken >= max }"><span :style="{ width: Math.min(100, (taken / max) * 100) + '%' }"></span></span>
    {{ taken }} of {{ max }} places used
  </span>
</template>
