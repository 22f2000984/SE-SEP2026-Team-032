<script setup>
import { computed, reactive } from 'vue';
import { checkInsOf, stateOf, flagged } from '../../services/checkins';
import { markReviewed } from '../../services/actions';
import { API_ON } from '../../services/api';
import { useDb } from '../../composables/useDb';
import { useToast } from '../../composables/useToast';
import { userName, when } from '../../utils/format';
import PageHeading from '../../components/common/PageHeading.vue';
import StatusPill from '../../components/common/StatusPill.vue';

const { db, commit } = useDb();
const { toast } = useToast();

const items = computed(() => flagged(db));
const active = computed(() => db.matches.filter(m => m.status === 'active'));
/* Live: the backend's email log (newest first). Preview: the emails recorded in the browser. */
const emails = computed(() => API_ON
  ? db.emails.slice(0, 6)
  : db.notifications.filter(n => n.email).slice(-6).reverse().map(n => ({ id: n.id, to: userName(db, n.userId), text: n.text, at: n.at })));
const notes = reactive({});

const matchOf = c => db.matches.find(m => m.id === c.matchId);
const writer = c => userName(db, matchOf(c)[c.by + 'Id']);
function progress(m) {
  const due = checkInsOf(db, m.id).filter(c => stateOf(c) !== 'upcoming');
  return `${due.filter(c => c.submittedAt).length} of ${due.length}`;
}
function latest(m) {
  const done = checkInsOf(db, m.id).filter(c => c.review);
  return done.length ? done[done.length - 1].review : null;
}
async function review(c) {
  const problem = await markReviewed(c.id, notes[c.id]);
  if (problem) { toast(problem); return; }
  commit();
  toast('Marked as reviewed');
}
</script>

<template>
  <PageHeading eyebrow="Admin" title="Mentorship Pulse" intro="Every active match has a check-in each week. Reminders are emailed, an AI agent reads the answers, and only the ones that need a person come here." />
  <div v-if="API_ON" class="notice">Each answer is reviewed by simple rules and, when the AI is switched on, by an AI agent that can only raise a verdict. It only flags. You decide what to do.</div>
  <div v-else class="notice">Design preview: here a simple offline stand-in gives the verdicts, so the flow can be shown. It only flags. You decide what to do.</div>

  <div class="card">
    <h2>Needs your review</h2>
    <p v-if="!items.length" class="muted">Nothing to review. Every answer so far looks fine.</p>
    <div v-for="c in items" :key="c.id" class="card inner">
      <b>{{ userName(db, matchOf(c).studentId) }} / {{ userName(db, matchOf(c).mentorId) }}</b> · week {{ c.week }} · from the {{ c.by }}, {{ writer(c) }}
      <p v-if="c.submittedAt">
        <StatusPill :value="c.review.verdict" /> <span class="muted">Rating {{ c.rating }}/5</span><br />
        “{{ c.comment || 'No comment' }}”<br /><span class="reasons">{{ c.review.source === 'ai' ? 'AI review' : 'Review' }}: {{ c.review.reason }}</span>
      </p>
      <p v-else><StatusPill value="overdue" /> <span class="muted">Due {{ when(c.dueAt) }} and still not answered.</span></p>
      <label class="sr-only" :for="'n' + c.id">Your note</label>
      <input :id="'n' + c.id" v-model="notes[c.id]" placeholder="What did you do? (optional note)" />
      <div class="actions"><button class="btn small" type="button" @click="review(c)">Mark reviewed</button></div>
    </div>
  </div>

  <div class="card" style="margin-top: 16px">
    <h2>Active mentorships</h2>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Student</th><th>Mentor</th><th>Check-ins answered</th><th>Latest AI verdict</th></tr></thead>
        <tbody>
          <tr v-for="m in active" :key="m.id">
            <td>{{ userName(db, m.studentId) }}</td>
            <td>{{ userName(db, m.mentorId) }}</td>
            <td>{{ progress(m) }} due</td>
            <td><StatusPill v-if="latest(m)" :value="latest(m).verdict" /><span v-else class="muted">none yet</span></td>
          </tr>
          <tr v-if="!active.length"><td colspan="4" class="muted">No active matches yet. Check-ins start when you confirm one.</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="card" style="margin-top: 16px">
    <h2>Emails sent</h2>
    <ul class="list">
      <li v-for="n in emails" :key="n.id"><b>To {{ n.to }}:</b> {{ n.text }} <span class="muted">· {{ when(n.at) }}<template v-if="n.status"> · {{ n.status === 'not_configured' ? 'not sent (no email key set)' : n.status }}</template></span></li>
      <li v-if="!emails.length" class="muted">No emails yet. The first ones go out when a match becomes active.</li>
    </ul>
    <p v-if="API_ON" class="muted">Emails go out through Brevo when its key is set. Otherwise they are only recorded here.</p>
    <p v-else class="muted">In this preview an email is only recorded here.</p>
  </div>
</template>
