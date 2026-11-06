<script setup>
import { computed, reactive, ref } from 'vue';
import { session } from '../../services/auth';
import { checkInsOf, stateOf, submitCheckIn } from '../../services/checkins';
import { useDb } from '../../composables/useDb';
import { useToast } from '../../composables/useToast';
import { userName, when } from '../../utils/format';
import StatusPill from '../common/StatusPill.vue';

/* The weekly check-ins of one person, one card for each active match. */
const props = defineProps({ role: { type: String, required: true } });
const { db, commit } = useDb();
const { toast } = useToast();
const me = session.value;
const other = props.role === 'student' ? 'mentor' : 'student';

const matches = computed(() => db.matches.filter(m => m[props.role + 'Id'] === me.id && m.status === 'active'));
const rows = m => checkInsOf(db, m.id, props.role);
/* Past and current weeks, then only the next one; the rest are summarised. */
const shown = m => { const all = rows(m), first = all.findIndex(c => stateOf(c) === 'upcoming'); return first < 0 ? all : all.slice(0, first + 1); };
const hidden = m => rows(m).length - shown(m).length;
const openRow = m => rows(m).find(c => ['due', 'overdue'].includes(stateOf(c)));
const emailOf = m => db.users.find(u => u.id === m[other + 'Id']).email;

const form = reactive({ rating: 5, comment: '' });
const error = ref('');

function send(c) {
  error.value = submitCheckIn(db, c.id, form) || '';
  if (error.value) return;
  commit();
  Object.assign(form, { rating: 5, comment: '' });
  toast('Check-in sent. Thank you.');
}
</script>

<template>
  <div v-if="!matches.length" class="info">Check-ins start when the admin confirms a match. We then send you an email at the end of every week.</div>
  <div v-for="m in matches" :key="m.id" class="card stack-gap">
    <h2>Mentorship with {{ userName(db, m[other + 'Id']) }}</h2>
    <p class="muted">Contact: {{ emailOf(m) }} (also sent to you by email). Agree session times and how you will talk with each other directly.</p>
    <p class="muted">There is one check-in for each week of the mentorship. Your answers go to the admin only; the other person does not see them.</p>

    <div class="table-wrap">
      <table>
        <thead><tr><th>Week</th><th>Due</th><th>Status</th><th>Your answer</th></tr></thead>
        <tbody>
          <tr v-for="c in shown(m)" :key="c.id">
            <td>Week {{ c.week }}</td>
            <td>{{ when(c.dueAt) }}</td>
            <td><StatusPill :value="stateOf(c)" /></td>
            <td><template v-if="c.submittedAt">{{ c.rating }}/5<br /><span class="muted">{{ c.comment || 'No comment' }}</span></template><span v-else class="muted">-</span></td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-if="hidden(m)" class="muted">{{ hidden(m) }} more week{{ hidden(m) > 1 ? 's' : '' }} follow, up to week {{ rows(m).length }}.</p>

    <div v-if="openRow(m)" class="card inner">
      <h2>Week {{ openRow(m).week }} check-in</h2>
      <form @submit.prevent="send(openRow(m))">
        <label for="rating">How is the mentorship going? (5 is best)</label>
        <select id="rating" v-model="form.rating"><option v-for="n in [5, 4, 3, 2, 1]" :key="n" :value="n">{{ n }}</option></select>
        <label for="comment">Anything the admin should know? (optional)</label>
        <textarea id="comment" v-model="form.comment" rows="3"></textarea>
        <div class="err" role="alert">{{ error }}</div>
        <div class="actions"><button class="btn" type="submit">Send check-in</button></div>
      </form>
    </div>
    <p v-else class="muted">No check-in is waiting. We will email you when the next one is due.</p>
  </div>
</template>
