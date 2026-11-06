<script setup>
import { computed } from 'vue';
import { NEXT_STEP } from '../../config/constants';
import { session } from '../../services/auth';
import { notificationsFor } from '../../services/notifications';
import { toAnswer } from '../../services/checkins';
import { useDb } from '../../composables/useDb';
import { latestMatchOf, userName } from '../../utils/format';
import PageHeading from '../../components/common/PageHeading.vue';
import StatusPill from '../../components/common/StatusPill.vue';
import NotificationList from '../../components/common/NotificationList.vue';

const { db } = useDb();
const me = session.value;
const profile = computed(() => db.students[me.id]);
const match = computed(() => latestMatchOf(db, me.id));
const answer = computed(() => (match.value && match.value.status === 'proposed' ? match.value.studentResponse : null));

const completeness = computed(() => {
  const p = profile.value;
  const checks = [p.programme, p.goals, p.skills, p.topics.length, p.preferences, p.availability];
  return Math.round((checks.filter(Boolean).length / checks.length) * 100);
});

const message = computed(() => {
  const m = match.value;
  if (!m) return 'The admin has not arranged a mentor for you yet. Complete your profile so they can find a good fit.';
  if (m.status === 'proposed') {
    if (answer.value === 'pending') return 'A mentor has been proposed for you. Please accept or decline.';
    if (answer.value === 'accepted') return 'You accepted. Waiting for the mentor and the admin to confirm.';
    return 'You declined. The admin will decide what happens next.';
  }
  if (m.status === 'cancelled') return 'Your last match was cancelled. The admin will arrange a new one.';
  return `Your mentor is ${userName(db, m.mentorId)}.`;
});
const nextStep = computed(() => (match.value ? NEXT_STEP[match.value.status] : 'Complete your profile so the admin can find a good fit.'));
const notes = computed(() => notificationsFor(db, me.id, 4));
const waiting = computed(() => toAnswer(db, me.id, 'student').length);
</script>

<template>
  <PageHeading eyebrow="Student" :title="`Welcome, ${me.name}`" intro="Your mentoring journey, in one place." />
  <div v-if="waiting" class="notice">You have {{ waiting }} weekly check-in{{ waiting > 1 ? 's' : '' }} to answer. <router-link to="/student/checkins">Answer now</router-link></div>
  <section class="grid">
    <div class="card">
      <h2>Match status</h2>
      <StatusPill :value="match ? (match.status === 'proposed' ? 'pending' : match.status) : 'none yet'" />
      <p>{{ message }}</p>
      <p class="muted"><b>Next step:</b> {{ nextStep }}</p>
      <router-link class="btn" to="/student/mentor">{{ answer === 'pending' ? 'Respond to proposal' : 'My mentor' }}</router-link>
    </div>
    <div class="card">
      <h2>Profile completeness</h2>
      <div class="metric">{{ completeness }}%</div>
      <div class="bar"><div :style="{ width: completeness + '%' }"></div></div>
      <p>{{ completeness < 100 ? 'Add your goals and availability to help the admin match you.' : 'Your profile is complete.' }}</p>
      <router-link class="btn ghost" to="/student/profile">Edit profile</router-link>
    </div>
  </section>
  <div class="card"><h2>Notifications</h2><NotificationList :items="notes" /></div>
</template>
