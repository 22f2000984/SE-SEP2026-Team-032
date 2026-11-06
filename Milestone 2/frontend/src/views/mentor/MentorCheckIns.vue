<script setup>
import PageHeading from '../../components/common/PageHeading.vue';
import CheckInPanel from '../../components/checkin/CheckInPanel.vue';
</script>

<template>
  <PageHeading eyebrow="Mentor" title="Weekly check-ins" intro="A short question every week for each mentee, so the admin can step in early if help is needed." />
  <CheckInPanel role="mentor" />
</template>
