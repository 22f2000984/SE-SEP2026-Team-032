<script setup>
import { computed, ref } from 'vue';
import { STATUSES } from '../../config/constants';
import { bothAccepted } from '../../services/matches';
import { waitingStudents } from '../../services/matching';
import { resolveConcern } from '../../services/feedback';
import { flagged } from '../../services/checkins';
import { notificationsFor } from '../../services/notifications';
import { session } from '../../services/auth';
import { useDb } from '../../composables/useDb';
import { useToast } from '../../composables/useToast';
import { userName, when } from '../../utils/format';
import PageHeading from '../../components/common/PageHeading.vue';
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
const flaggedCheckIns = computed(() => flagged(db));
const openConcerns = computed(() => db.concerns.filter(c => c.status === 'open'));
const recentFeedback = computed(() => db.feedback.slice(-5).reverse());
const notes = computed(() => notificationsFor(db, me.id, 6));
const count = status => db.matches.filter(m => m.status === status).length;
const studentCount = computed(() => db.users.filter(u => u.role === 'student').length);

/* Everything that needs the admin, one line each. */
const todo = computed(() => [
  { label: 'matches ready to confirm', count: ready.value.length, to: '/admin/matches', cta: 'Confirm' },
  { label: 'proposals declined by one side', count: declined.value.length, to: '/admin/matches', cta: 'Decide' },
  { label: 'mentors waiting to be verified', count: pending.value.length, to: '/admin/mentors', cta: 'Review' },
  { label: 'students waiting for a match', count: waiting.value.length, to: '/admin/matches', cta: 'Match' },
  { label: 'proposals waiting more than 3 days', count: delayed.value.length, to: '/admin/matches', cta: 'Open' },
  { label: 'weekly check-ins flagged for review', count: flaggedCheckIns.value.length, to: '/admin/pulse', cta: 'Review' },
  { label: 'open concerns', count: openConcerns.value.length, tab: 'concerns', cta: 'View' }
]);

/* The secondary information, one panel at a time. */
const tab = ref('concerns');
const tabs = computed(() => [
  { key: 'concerns', label: 'Open concerns', count: openConcerns.value.length },
  { key: 'feedback', label: 'Student feedback', count: db.feedback.length },
  { key: 'capacity', label: 'Mentor capacity' },
  { key: 'activity', label: 'Recent activity' }
]);

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
  <PageHeading eyebrow="Admin" title="Overview" />
  <p class="summary muted">
    <span v-for="s in STATUSES" :key="s" class="summary-item"><StatusPill :value="s" /> {{ count(s) }}</span>
    <span class="summary-item">{{ studentCount }} students · {{ Object.keys(db.mentors).length }} mentors</span>
  </p>

  <div class="card">
    <h2>Needs your attention</h2>
    <ul class="todo-list">
      <li v-for="item in todo" :key="item.label" class="todo" :class="{ clear: !item.count }">
        <span class="todo-count">{{ item.count }}</span>
        <span class="todo-label">{{ item.label }}</span>
        <router-link v-if="item.count && item.to" class="btn small ghost" :to="item.to">{{ item.cta }}</router-link>
        <button v-else-if="item.count && item.tab" class="btn small ghost" type="button" @click="tab = item.tab">{{ item.cta }}</button>
      </li>
    </ul>
  </div>

  <div class="card" style="margin-top: 16px">
    <h2>Recommended matches</h2>
    <p class="muted">The best mentor for each waiting student, with a Smart Match score out of 100. <router-link to="/admin/matches">See the top 3</router-link></p>
    <RecommendationTable :per-student="1" compact />
  </div>

  <div class="card" style="margin-top: 16px">
    <div class="tabs" role="tablist">
      <button v-for="t in tabs" :key="t.key" class="tab" :class="{ active: tab === t.key }" type="button" role="tab" :aria-selected="tab === t.key" @click="tab = t.key">
        {{ t.label }}<span v-if="t.count" class="tab-count">{{ t.count }}</span>
      </button>
    </div>

    <div v-if="tab === 'concerns'" role="tabpanel">
      <ul class="list">
        <li v-for="c in openConcerns" :key="c.id">{{ userName(db, c.raisedBy) }}: {{ c.text }}<div class="actions"><button class="btn small" type="button" @click="resolve(c.id)">Mark resolved</button></div></li>
        <li v-if="!openConcerns.length" class="muted">No open concerns.</li>
      </ul>
    </div>
    <div v-else-if="tab === 'feedback'" role="tabpanel">
      <ul class="list">
        <li v-for="f in recentFeedback" :key="f.id"><b>{{ f.rating }}/5</b> · {{ userName(db, f.authorId) }} about {{ mentorOf(f) }}<br /><span class="muted">{{ f.comments || 'No comment' }} · {{ when(f.at) }}</span></li>
        <li v-if="!recentFeedback.length" class="muted">No feedback yet.</li>
      </ul>
    </div>
    <div v-else-if="tab === 'capacity'" role="tabpanel">
      <ul class="list">
        <li v-for="(m, id) in db.mentors" :key="id"><b>{{ userName(db, Number(id)) }}</b> <StatusPill :value="m.status" /><br /><CapacityBar :mentor-id="Number(id)" /></li>
      </ul>
    </div>
    <div v-else role="tabpanel"><NotificationList :items="notes" empty="None." /></div>
  </div>
</template>

<style scoped>
.summary { display: flex; flex-wrap: wrap; gap: 6px 18px; align-items: center; margin: 0 0 18px; font-size: 14px; }
.summary-item { display: inline-flex; align-items: center; gap: 6px; }
.todo-list { list-style: none; margin: 0; padding: 0; }
.todo { display: grid; grid-template-columns: 44px 1fr auto; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--line-soft); }
.todo:last-child { border-bottom: 0; }
.todo-count { display: inline-flex; align-items: center; justify-content: center; width: 34px; height: 34px; border-radius: 50%; background: #fff1d9; color: var(--warn); font-weight: 850; }
.todo.clear .todo-count { background: var(--lilac); color: var(--muted); }
.todo.clear .todo-label { color: var(--muted); }
</style>
