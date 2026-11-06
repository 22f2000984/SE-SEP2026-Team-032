<script setup>
import { computed } from 'vue';
import { MIN_SCORE } from '../../config/constants';
import { waitingStudents } from '../../services/matching';
import { recommendSmart } from '../../services/smartMatch';
import { proposeMatch } from '../../services/matches';
import { useDb } from '../../composables/useDb';
import { useToast } from '../../composables/useToast';
import { session } from '../../services/auth';
import { topicsText, userName } from '../../utils/format';
import ScoreBar from '../common/ScoreBar.vue';

/* For each student without a match: the best mentors, each with a score and the reasons. */
/* compact: fewer columns (the reasons sit under the mentor's name), used on the overview. */
const props = defineProps({ perStudent: { type: Number, default: 1 }, compact: { type: Boolean, default: false } });
const { db, commit } = useDb();
const { toast } = useToast();

const rows = computed(() => waitingStudents(db).map(student => ({ student, recs: recommendSmart(db, student.id, props.perStudent) })));

function propose(studentId, mentorId) {
  const error = proposeMatch(db, studentId, mentorId, 'Recommended by Smart Match', session.value.name);
  if (error) { toast(error); return; }
  commit();
  toast('Match proposed. Both people were notified.');
}
</script>

<template>
  <p v-if="!rows.length" class="muted">Every student has an open match.</p>
  <div v-else class="table-wrap">
    <table>
      <thead><tr><th>Waiting student</th><th>Recommended mentor</th><th>Smart Match score</th><th v-if="!compact">Why</th><th></th></tr></thead>
      <tbody v-for="row in rows" :key="row.student.id">
        <tr v-if="!row.recs.length">
          <td><b>{{ row.student.name }}</b></td>
          <td :colspan="compact ? 3 : 4" class="muted">No eligible mentor right now (unverified or full).</td>
        </tr>
        <tr v-for="(r, i) in row.recs" :key="r.mentorId">
          <td v-if="i === 0" :rowspan="row.recs.length"><b>{{ row.student.name }}</b><br /><span class="muted">{{ topicsText(db.students[row.student.id].topics) }}</span></td>
          <td>
            {{ userName(db, r.mentorId) }}<br />
            <span v-if="compact" class="reasons">{{ r.reason }}</span>
            <span v-else class="muted">{{ topicsText(db.mentors[r.mentorId].topics) }}</span>
          </td>
          <td><ScoreBar :total="r.total" /><template v-if="r.total < MIN_SCORE"><br /><span class="muted">weak fit</span></template></td>
          <td v-if="!compact" class="reasons">{{ r.reason }}<div class="muted">Rule score (topics and experience): {{ r.ruleTotal }}</div></td>
          <td><button class="btn small" type="button" @click="propose(row.student.id, r.mentorId)">Propose</button></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
