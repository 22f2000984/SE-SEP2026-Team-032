<script setup>
import { computed } from 'vue';
import { session } from '../../services/auth';
import { respond, bothAccepted } from '../../services/matches';
import { notificationsFor } from '../../services/notifications';
import { useDb } from '../../composables/useDb';
import { useToast } from '../../composables/useToast';
import { userName, topicsText, when } from '../../utils/format';
import PageHeading from '../../components/common/PageHeading.vue';
import StatusPill from '../../components/common/StatusPill.vue';
import CapacityBar from '../../components/common/CapacityBar.vue';
import NotificationList from '../../components/common/NotificationList.vue';

const { db, commit } = useDb();
const { toast } = useToast();
const me = session.value;

const profile = computed(() => db.mentors[me.id]);
const mine = computed(() => db.matches.filter(m => m.mentorId === me.id));
const requests = computed(() => mine.value.filter(m => m.status === 'proposed'));
const mentees = computed(() => mine.value.filter(m => m.status === 'active'));
const notes = computed(() => notificationsFor(db, me.id, 4));

function answer(match, value) {
  respond(db, match, 'mentor', value);
  commit();
  toast(value === 'accepted' ? 'You accepted the request' : 'You declined the request');
}
</script>

<template>
  <PageHeading eyebrow="Mentor" :title="`Welcome, ${me.name}`" />
  <div v-if="profile.status !== 'verified'" class="notice">Your profile is pending verification by the admin. You will receive matches after it is verified.</div>

  <div class="card">
    <h2>Match requests</h2>
    <div v-for="m in requests" :key="m.id" class="card inner">
      <b>{{ userName(db, m.studentId) }}</b> · proposed {{ when(m.proposedAt) }}<br />
      <span class="muted">
        Goals: {{ db.students[m.studentId].goals || 'not added yet' }} · Programme: {{ db.students[m.studentId].programme || '-' }} ·
        Topics: {{ topicsText(db.students[m.studentId].topics) }} · Format: {{ db.students[m.studentId].format || '-' }} · Duration: {{ db.students[m.studentId].duration || '-' }}
      </span>
      <p>Your response: <StatusPill :value="m.mentorResponse" /> &nbsp; Student's response: <StatusPill :value="m.studentResponse" /></p>
      <div v-if="m.mentorResponse === 'pending'" class="actions">
        <button class="btn small" type="button" @click="answer(m, 'accepted')">Accept</button>
        <button class="btn small danger" type="button" @click="answer(m, 'declined')">Decline</button>
      </div>
      <p v-else class="muted">{{ bothAccepted(m) ? 'Both of you accepted. The admin will confirm the match.' : 'The admin confirms the match once both of you have accepted.' }}</p>
    </div>
    <p v-if="!requests.length" class="muted">No pending requests.</p>
  </div>

  <div class="card" style="margin-top: 16px">
    <h2>My mentees</h2>
    <p class="muted"><CapacityBar :mentor-id="me.id" /></p>
    <ul class="list">
      <li v-for="m in mentees" :key="m.id"><b>{{ userName(db, m.studentId) }}</b> <StatusPill :value="m.status" /><br /><span class="muted">{{ db.students[m.studentId].goals }}</span></li>
      <li v-if="!mentees.length" class="muted">No mentees yet.</li>
    </ul>
  </div>

  <div class="card" style="margin-top: 16px"><h2>Notifications</h2><NotificationList :items="notes" empty="None." /></div>
</template>
