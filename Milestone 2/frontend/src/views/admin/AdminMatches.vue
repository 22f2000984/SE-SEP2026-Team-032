<script setup>
import { computed, ref, watch } from 'vue';
import { NEXT, MIN_SCORE } from '../../config/constants';
import { waitingStudents, used, maxOf } from '../../services/matching';
import { proposeMatch, setStatus, bothAccepted } from '../../services/matches';
import { session } from '../../services/auth';
import { useDb } from '../../composables/useDb';
import { useToast } from '../../composables/useToast';
import { userName, when } from '../../utils/format';
import PageHeading from '../../components/common/PageHeading.vue';
import StatusPill from '../../components/common/StatusPill.vue';
import ScoreBar from '../../components/common/ScoreBar.vue';
import RecommendationTable from '../../components/match/RecommendationTable.vue';
import MatchCompare from '../../components/match/MatchCompare.vue';

const { db, commit } = useDb();
const { toast } = useToast();
const me = session.value;

const students = computed(() => waitingStudents(db));
const mentors = computed(() => db.users.filter(u => u.role === 'mentor' && db.mentors[u.id].status === 'verified'));
const studentId = ref(null);
const mentorId = ref(null);
const notes = ref('');
const error = ref('');

/* Keep the selected student and mentor valid as the lists change. */
watch([students, mentors], () => {
  if (!students.value.some(s => s.id === studentId.value)) studentId.value = students.value.length ? students.value[0].id : null;
  if (!mentors.value.some(m => m.id === mentorId.value)) mentorId.value = mentors.value.length ? mentors.value[0].id : null;
}, { immediate: true });

function propose() {
  if (!studentId.value || !mentorId.value) { error.value = 'Choose a student and a verified mentor.'; return; }
  error.value = proposeMatch(db, studentId.value, mentorId.value, notes.value.trim(), me.name) || '';
  if (error.value) return;
  commit();
  notes.value = '';
  toast('Match proposed');
}
function confirm(m) {
  if (setStatus(db, m, 'active', me.name)) { commit(); toast('Match confirmed'); }
}
function cancel(m) {
  setStatus(db, m, 'cancelled', me.name);
  commit();
  toast('Match cancelled');
}
function change(m, event) {
  const to = event.target.value;
  if (!to) return;
  setStatus(db, m, to, me.name);
  commit();
  toast('Status updated');
}
</script>

<template>
  <PageHeading eyebrow="Admin" title="Matches" />

  <div class="card">
    <h2>Recommended matches</h2>
    <p class="muted">
      Smart Match reads what each student and mentor wrote about their needs and skills, and scores every waiting student against each verified mentor with free places, out of 100.
      Unverified mentors and mentors who are full are not shown. A score under {{ MIN_SCORE }} is a weak fit. It only suggests; you decide.
    </p>
    <p class="muted">Design preview: the AI agent is built in Sprint 1. This page uses an offline stand-in that compares the wording of the two texts and the topics and experience, and gives the same kind of score and reason.</p>
    <RecommendationTable :per-student="3" />
  </div>

  <div class="card" style="margin-top: 16px">
    <h2>Propose a match yourself</h2>
    <p class="muted">Both the mentor and the student are notified. You can confirm the match only after both have accepted, or you can cancel it.</p>
    <form @submit.prevent="propose">
      <div class="row">
        <div>
          <label for="s">Student without a match</label>
          <select id="s" v-model="studentId"><option v-for="s in students" :key="s.id" :value="s.id">{{ s.name }}</option></select>
        </div>
        <div>
          <label for="m">Verified mentor</label>
          <select id="m" v-model="mentorId"><option v-for="m in mentors" :key="m.id" :value="m.id">{{ m.name }} ({{ used(db, m.id) }} of {{ maxOf(db, m.id) }} places used)</option></select>
        </div>
      </div>
      <MatchCompare :student-id="studentId" :mentor-id="mentorId" />
      <label for="n">Notes (the basis for this match)</label>
      <input id="n" v-model="notes" placeholder="Why this pairing?" />
      <div class="err" role="alert">{{ error }}</div>
      <div class="actions"><button class="btn" type="submit">Propose match</button></div>
    </form>
  </div>

  <h2 style="margin-top: 24px">All matches</h2>
  <div class="table-wrap">
    <table>
      <thead><tr><th>Student</th><th>Mentor</th><th>Status</th><th>Smart Match</th><th>Mentor response</th><th>Student response</th><th>Proposed</th><th>Action</th></tr></thead>
      <tbody>
        <tr v-for="m in db.matches" :key="m.id">
          <td>{{ userName(db, m.studentId) }}</td>
          <td>{{ userName(db, m.mentorId) }}</td>
          <td><StatusPill :value="m.status" /><br /><span class="muted">{{ m.log.length }} update(s)</span></td>
          <td><ScoreBar v-if="m.smartScore != null" :total="m.smartScore" /><span v-else>-</span></td>
          <td>
            <template v-if="m.status === 'proposed'"><StatusPill :value="m.mentorResponse" /><template v-if="m.mentorRespondedAt"><br /><span class="muted">{{ when(m.mentorRespondedAt) }}</span></template></template>
            <span v-else class="muted">-</span>
          </td>
          <td>
            <template v-if="m.status === 'proposed'"><StatusPill :value="m.studentResponse" /><template v-if="m.studentRespondedAt"><br /><span class="muted">{{ when(m.studentRespondedAt) }}</span></template></template>
            <span v-else class="muted">-</span>
          </td>
          <td>{{ when(m.proposedAt) }}</td>
          <td>
            <div v-if="m.status === 'proposed'" class="actions">
              <button class="btn small" type="button" :disabled="!bothAccepted(m)" :title="bothAccepted(m) ? '' : 'Both sides must accept first'" @click="confirm(m)">Confirm match</button>
              <button class="btn small danger" type="button" @click="cancel(m)">Cancel</button>
            </div>
            <select v-else-if="NEXT[m.status].length" :aria-label="'Change status of match ' + m.id" @change="change(m, $event)">
              <option value="">Choose…</option>
              <option v-for="s in NEXT[m.status]" :key="s">{{ s }}</option>
            </select>
            <span v-else class="muted">Final</span>
          </td>
        </tr>
        <tr v-if="!db.matches.length"><td colspan="8" class="muted">No matches yet.</td></tr>
      </tbody>
    </table>
  </div>
</template>
