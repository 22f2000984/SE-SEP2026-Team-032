<script setup>
import { computed, ref } from 'vue';
import { TOPICS } from '../../config/constants';
import { useDb } from '../../composables/useDb';
import { latestMatchOf, when } from '../../utils/format';
import PageHeading from '../../components/common/PageHeading.vue';
import StatusPill from '../../components/common/StatusPill.vue';
import TopicChips from '../../components/common/TopicChips.vue';

const { db } = useDb();
const q = ref('');
const programme = ref('');
const topic = ref('');
const response = ref('');

const students = computed(() => db.users.filter(u => u.role === 'student'));
const programmes = computed(() => [...new Set(students.value.map(u => db.students[u.id].programme).filter(Boolean))]);
const rows = computed(() => students.value.filter(u => {
  const p = db.students[u.id], last = latestMatchOf(db, u.id);
  const haystack = [u.name, p.goals, p.skills, p.topics.join(' '), p.preferences].join(' ').toLowerCase();
  return (!q.value || haystack.includes(q.value.toLowerCase()))
    && (!programme.value || p.programme === programme.value)
    && (!topic.value || p.topics.includes(topic.value))
    && (!response.value || (last ? last.studentResponse : 'none') === response.value);
}));
const lastMatch = id => latestMatchOf(db, id);
</script>

<template>
  <PageHeading eyebrow="Admin" title="Students" intro="Review student needs before proposing a match. Only the admin can see these profiles." />
  <div class="card">
    <div class="row">
      <div><label for="q">Search name, goal, skill or topic</label><input id="q" v-model="q" placeholder="e.g. analytics" /></div>
      <div class="row">
        <div><label for="prog">Programme level</label><select id="prog" v-model="programme"><option value="">All</option><option v-for="p in programmes" :key="p">{{ p }}</option></select></div>
        <div><label for="topic">Topic</label><select id="topic" v-model="topic"><option value="">All</option><option v-for="t in TOPICS" :key="t">{{ t }}</option></select></div>
      </div>
    </div>
    <div style="max-width: 320px">
      <label for="resp">Response to proposal</label>
      <select id="resp" v-model="response">
        <option value="">All</option><option value="pending">pending</option><option value="accepted">accepted</option><option value="declined">declined</option><option value="none">no proposal</option>
      </select>
    </div>
  </div>

  <div class="table-wrap" style="margin-top: 16px">
    <table>
      <thead><tr><th>Student</th><th>Programme</th><th>Goals and needs</th><th>Mentoring preferences</th><th>Response to proposal</th><th>Match</th></tr></thead>
      <tbody>
        <tr v-for="u in rows" :key="u.id">
          <td><b>{{ u.name }}</b><br /><span class="muted">{{ u.email }}</span></td>
          <td>{{ db.students[u.id].programme || '-' }}</td>
          <td>{{ db.students[u.id].goals || 'not added yet' }}<br /><span class="muted">Skills: {{ db.students[u.id].skills || '-' }}</span></td>
          <td>
            <TopicChips :topics="db.students[u.id].topics" /><br />
            <span class="muted">Format:</span> {{ db.students[u.id].format || '-' }} · <span class="muted">Duration:</span> {{ db.students[u.id].duration || '-' }}<br />
            <span class="muted">Available:</span> {{ db.students[u.id].availability || '-' }}
          </td>
          <td>
            <template v-if="lastMatch(u.id) && lastMatch(u.id).status !== 'cancelled'">
              <StatusPill :value="lastMatch(u.id).studentResponse" />
              <template v-if="lastMatch(u.id).studentRespondedAt"><br /><span class="muted">{{ when(lastMatch(u.id).studentRespondedAt) }}</span></template>
            </template>
            <span v-else class="muted">none</span>
          </td>
          <td><StatusPill v-if="lastMatch(u.id)" :value="lastMatch(u.id).status" /><span v-else class="muted">none</span></td>
        </tr>
        <tr v-if="!rows.length"><td colspan="6" class="muted">No students match the filters.</td></tr>
      </tbody>
    </table>
  </div>
</template>
