<script setup>
import PageHeading from '../../components/common/PageHeading.vue';
import CheckInPanel from '../../components/checkin/CheckInPanel.vue';
</script>

<template>
  <PageHeading eyebrow="Student" title="Weekly check-ins" intro="A short question every week, so the admin knows your mentorship is going well." />
  <CheckInPanel role="student" />
</template>
