<script setup>
import { computed } from 'vue';
import { MIN_SCORE } from '../../config/constants';
import { eligible } from '../../services/matching';
import { smartScore } from '../../services/smartMatch';
import { slotText } from '../../services/profiles';
import { API_ON } from '../../services/api';
import { useDb } from '../../composables/useDb';
import { topicsText } from '../../utils/format';
import ScoreBar from '../common/ScoreBar.vue';
import CapacityBar from '../common/CapacityBar.vue';

/* The student's needs next to the mentor's offer, with the score of this pair. */
const props = defineProps({ studentId: Number, mentorId: Number });
const { db } = useDb();
const student = computed(() => db.students[props.studentId]);
const mentor = computed(() => db.mentors[props.mentorId]);
const score = computed(() => (student.value && mentor.value ? smartScore(db, props.studentId, props.mentorId) : null));
const problem = computed(() => (score.value ? eligible(db, props.studentId, props.mentorId) : null));
</script>

<template>
  <div v-if="score">
    <div class="sidebyside">
      <div class="card">
        <h2>Student needs</h2>
        <dl>
          <dt>Goals</dt><dd>{{ student.goals || 'not added yet' }}</dd>
          <dt>In their own words</dt><dd>{{ student.needsText || 'not written yet' }}</dd>
          <dt>Topics wanted</dt><dd>{{ topicsText(student.topics) }}</dd>
          <dt>Skills</dt><dd>{{ student.skills || '-' }}</dd>
          <template v-if="Object.keys(student.levels || {}).length"><dt>Level (quiz)</dt><dd><div v-for="(level, name) in student.levels" :key="name">{{ name }}: {{ level }}</div></dd></template>
          <dt>Format and duration</dt><dd>{{ student.format || '-' }} · {{ student.duration || '-' }}</dd>
          <dt>Availability</dt><dd>{{ student.availability || '-' }}</dd>
        </dl>
      </div>
      <div class="card">
        <h2>Mentor offer</h2>
        <dl>
          <dt>Qualifications</dt><dd>{{ mentor.qualifications || '-' }} · {{ mentor.experience }} yrs</dd>
          <dt>Topics covered</dt><dd>{{ topicsText(mentor.topics) }}</dd>
          <dt>In their own words</dt><dd>{{ mentor.skillsText || 'not written yet' }}</dd>
          <dt>Bio</dt><dd>{{ mentor.bio || '-' }}</dd>
          <dt>Availability</dt><dd>{{ slotText(db, mentorId) }}</dd>
          <dt>Capacity</dt><dd><CapacityBar :mentor-id="mentorId" /></dd>
        </dl>
      </div>
    </div>
    <div class="info">
      <b>{{ API_ON ? 'Quick estimate:' : 'Smart Match score:' }}</b> <ScoreBar :total="score.total" /> &nbsp;
      <span class="muted">rule score (topics and experience) {{ score.ruleTotal }}/100</span><br />
      {{ score.reason }}
      <template v-if="API_ON"><br /><span class="muted">Worked out in your browser. The Smart Match scores are in the table above.</span></template>
      <template v-if="score.total < MIN_SCORE"><br /><b>Weak fit.</b> You can still propose it.</template>
      <template v-if="problem"><br /><b>{{ problem }}</b></template>
    </div>
  </div>
</template>
