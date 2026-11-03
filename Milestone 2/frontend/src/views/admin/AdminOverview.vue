<script setup>
import { computed } from 'vue';
import { STATUSES } from '../../config/constants';
import { bothAccepted } from '../../services/matches';
import { waitingStudents } from '../../services/matching';
import { resolveConcern } from '../../services/feedback';
import { notificationsFor } from '../../services/notifications';
import { session } from '../../services/auth';
import { useDb } from '../../composables/useDb';
import { useToast } from '../../composables/useToast';
import { userName, when } from '../../utils/format';
import PageHeading from '../../components/common/PageHeading.vue';
import StatCard from '../../components/common/StatCard.vue';
import StatusPill from '../../components/common/StatusPill.vue';
import CapacityBar from '../../components/common/CapacityBar.vue';
import NotificationList from '../../components/common/NotificationList.vue';
import RecommendationTable from '../../components/match/RecommendationTable.vue';

const { db, commit } = useDb();
const { toast } = useToast();
const me = session.value;

const proposed = computed(() => db.matches.filter(m => m.status === 'proposed'));
const ready = computed(() => proposed.value.filter(bothAccepted));
const declined = computed(() => proposed.value.filter(m => m.mentorResponse === 'declined' || m.studentResponse === 'declined'));
const delayed = computed(() => proposed.value.filter(m => Date.now() - new Date(m.proposedAt) > 3 * 864e5));
const pending = computed(() => Object.values(db.mentors).filter(m => m.status === 'pending'));
const waiting = computed(() => waitingStudents(db));
const openConcerns = computed(() => db.concerns.filter(c => c.status === 'open'));
const count = status => db.matches.filter(m => m.status === status).length;
const recentFeedback = computed(() => db.feedback.slice(-5).reverse());
const notes = computed(() => notificationsFor(db, me.id, 5));
const studentCount = computed(() => db.users.filter(u => u.role === 'student').length);

function resolve(id) {
  resolveConcern(db, id);
  commit();
  toast('Concern resolved');
}
function mentorOf(feedback) {
  const m = db.matches.find(x => x.id === feedback.matchId);
  return m ? userName(db, m.mentorId) : 'a mentor';
}
</script>

<template>
  <PageHeading eyebrow="Admin" title="Overview" intro="What needs your attention first, then the recommended matches." />

  <section class="stats">
    <StatCard :count="ready.length" label="matches ready to confirm" to="/admin/matches" cta="confirm" />
    <StatCard :count="declined.length" label="proposals declined by a side" to="/admin/matches" cta="decide" />
    <StatCard :count="pending.length" label="mentors to verify" to="/admin/mentors" cta="review" />
    <StatCard :count="waiting.length" label="students waiting for a match" to="/admin/matches" cta="match" />
    <StatCard :count="openConcerns.length" label="open concerns" />
  </section>

  <div class="card">
    <h2>Recommended matches</h2>
    <p class="muted">Best mentor for each waiting student, scored out of 100. <router-link to="/admin/matches">See top 3 and more</router-link></p>
    <RecommendationTable :per-student="1" />
  </div>

  <section class="grid-2">
    <div class="card">
      <h2>Mentor capacity</h2>
      <ul class="list">
        <li v-for="(m, id) in db.mentors" :key="id"><b>{{ userName(db, Number(id)) }}</b> <StatusPill :value="m.status" /><br /><CapacityBar :mentor-id="Number(id)" /></li>
      </ul>
    </div>
    <div class="card">
      <h2>Matches by status</h2>
      <div class="status-row"><div v-for="s in STATUSES" :key="s"><StatusPill :value="s" /><div class="metric">{{ count(s) }}</div></div></div>
      <p class="muted">{{ studentCount }} student profiles · {{ Object.keys(db.mentors).length }} mentor profiles<template v-if="delayed.length"> · {{ delayed.length }} proposal(s) waiting more than 3 days</template></p>
    </div>
  </section>

  <section class="grid-2">
    <div class="card" id="concerns">
      <h2>Open concerns</h2>
      <ul class="list">
        <li v-for="c in openConcerns" :key="c.id">{{ userName(db, c.raisedBy) }}: {{ c.text }}<div class="actions"><button class="btn small" type="button" @click="resolve(c.id)">Mark resolved</button></div></li>
        <li v-if="!openConcerns.length" class="muted">No open concerns.</li>
      </ul>
    </div>
    <div class="card">
      <h2>Student feedback</h2>
      <ul class="list">
        <li v-for="f in recentFeedback" :key="f.id"><b>{{ f.rating }}/5</b> · {{ userName(db, f.authorId) }} about {{ mentorOf(f) }}<br /><span class="muted">{{ f.comments || 'No comment' }} · {{ when(f.at) }}</span></li>
        <li v-if="!recentFeedback.length" class="muted">No feedback yet.</li>
      </ul>
    </div>
  </section>

  <div class="card"><h2>Recent notifications</h2><NotificationList :items="notes" empty="None." /></div>
</template>

<style scoped>
.status-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 8px 0; }
@media (max-width: 600px) { .status-row { grid-template-columns: repeat(2, 1fr); } }
</style>
