<script setup>
/* variant "light" is for dark backgrounds, "dark" is for the white header. */
defineProps({ variant: { type: String, default: 'dark' } });
</script>

<template>
  <svg viewBox="0 0 80 70" aria-hidden="true">
    <path d="M8 33C10 12 28 2 43 5c16 2 27 14 29 29" fill="none" stroke="#ffc56f" stroke-width="4" stroke-linecap="round" />
    <path d="M13 51c8-12 18-17 27-17s20 5 28 17c-11-5-20-5-28 1-9-6-18-6-27-1Z" fill="#f7c46f" />
    <path d="M17 50c7-9 15-13 23-13v18c-8-7-15-8-23-5Zm23-13c9 0 17 4 24 13-8-3-16-2-24 5Z" :fill="variant === 'light' ? '#fff' : '#54216f'" />
    <circle cx="28" cy="27" r="7" :fill="variant === 'light' ? '#fff' : '#54216f'" />
    <circle cx="51" cy="25" r="6" :fill="variant === 'light' ? '#fff' : '#54216f'" />
  </svg>
</template>
