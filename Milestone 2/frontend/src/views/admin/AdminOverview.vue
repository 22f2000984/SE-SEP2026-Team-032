<script setup>
import { computed } from 'vue';
import { bothAccepted } from '../../services/matches';
import { waitingStudents } from '../../services/matching';
import { resolveConcern } from '../../services/feedback';
import { flagged } from '../../services/checkins';
import { notificationsFor } from '../../services/notifications';
import { matchCounts, pulseSummary, feedbackSummary, capacitySummary, peopleSummary } from '../../services/analytics';
import { session } from '../../services/auth';
import { useDb } from '../../composables/useDb';
import { useToast } from '../../composables/useToast';
import { userName, when } from '../../utils/format';
import PageHeading from '../../components/common/PageHeading.vue';
import NotificationList from '../../components/common/NotificationList.vue';
import RecommendationTable from '../../components/match/RecommendationTable.vue';
import StatCard from '../../components/dashboard/StatCard.vue';
import DonutChart from '../../components/dashboard/DonutChart.vue';

const { db, commit } = useDb();
const { toast } = useToast();
const me = session.value;

/* Everything on this page is counted from the data when the page opens or the data changes. */
const people = computed(() => peopleSummary(db));
const matches = computed(() => matchCounts(db));
const pulse = computed(() => pulseSummary(db));
const feedback = computed(() => feedbackSummary(db));
const capacity = computed(() => capacitySummary(db));
const countOf = status => matches.value.find(m => m.status === status).count;

const COLOURS = { proposed: '#e0a53a', active: '#4f9d6b', completed: '#8c50ae', cancelled: '#c0566b' };
const matchParts = computed(() => matches.value.map(m => ({ label: m.status, value: m.count, color: COLOURS[m.status] })));

const pulseRows = computed(() => [
  { label: 'On track', value: pulse.value.onTrack, color: '#4f9d6b' },
  { label: 'Watch', value: pulse.value.watch, color: '#e0a53a' },
  { label: 'Needs attention', value: pulse.value.needsAttention, color: '#c0566b' },
  { label: 'Not answered', value: pulse.value.unanswered, color: '#b7aac6' }
]);
const share = (value, total) => (total ? (value / total) * 100 : 0) + '%';

const proposed = computed(() => db.matches.filter(m => m.status === 'proposed'));
const attention = computed(() => [
  { label: 'matches ready to confirm', count: proposed.value.filter(bothAccepted).length, to: '/admin/matches', cta: 'Confirm' },
  { label: 'proposals declined by one side', count: proposed.value.filter(m => m.mentorResponse === 'declined' || m.studentResponse === 'declined').length, to: '/admin/matches', cta: 'Decide' },
  { label: 'mentors waiting to be verified', count: people.value.pending, to: '/admin/mentors', cta: 'Review' },
  { label: 'students waiting for a match', count: waitingStudents(db).length, to: '/admin/matches', cta: 'Match' },
  { label: 'proposals waiting more than 3 days', count: proposed.value.filter(m => Date.now() - new Date(m.proposedAt) > 3 * 864e5).length, to: '/admin/matches', cta: 'Open' },
  { label: 'weekly check-ins flagged for review', count: flagged(db).length, to: '/admin/pulse', cta: 'Review' }
]);
const attentionTotal = computed(() => attention.value.reduce((s, a) => s + a.count, 0) + openConcerns.value.length);

const openConcerns = computed(() => db.concerns.filter(c => c.status === 'open'));
const recentFeedback = computed(() => db.feedback.slice(-4).reverse());
const notes = computed(() => notificationsFor(db, me.id, 4));

function resolve(id) {
  resolveConcern(db, id);
  commit();
  toast('Concern resolved');
}
function mentorOf(f) {
  const m = db.matches.find(x => x.id === f.matchId);
  return m ? userName(db, m.mentorId) : 'a mentor';
}
</script>

<template>
  <PageHeading eyebrow="Admin" title="Overview" />
  <p class="muted dash-intro">What is going on across the platform: people, matches, mentorship health and what needs you.</p>

  <section class="stats" aria-label="Key numbers">
    <StatCard label="Students" :value="people.students" :sub="people.waiting + ' waiting for a match'" tone="violet" to="/admin/students" />
    <StatCard label="Mentors" :value="people.mentors" :sub="people.pending ? people.pending + ' to verify' : 'all verified'" tone="blue" to="/admin/mentors" />
    <StatCard label="Active mentorships" :value="countOf('active')" :sub="countOf('proposed') + ' proposed, ' + countOf('completed') + ' completed'" tone="green" to="/admin/matches" />
    <StatCard label="Check-in response" :value="pulse.asked ? pulse.responseRate : '-'" :unit="pulse.asked ? '%' : ''"
      :sub="pulse.asked ? pulse.answered + ' of ' + pulse.asked + ' answered' : 'none due yet'" tone="gold" to="/admin/pulse" />
    <StatCard label="Average rating" :value="feedback.average === null ? '-' : feedback.average" :unit="feedback.average === null ? '' : '/ 5'"
      :sub="feedback.total + ' feedback from students'" tone="violet" />
    <StatCard label="Needs you" :value="attentionTotal" :sub="attentionTotal ? 'see the list below' : 'all clear'" :tone="attentionTotal ? 'rose' : 'green'" />
  </section>

  <div class="panels cols-2">
    <div class="card panel">
      <h2>Needs your attention</h2>
      <ul class="attn">
        <li v-for="a in attention" :key="a.label" :class="{ clear: !a.count }">
          <span class="n">{{ a.count }}</span>
          <span>{{ a.label }}</span>
          <router-link v-if="a.count" class="btn small ghost" :to="a.to">{{ a.cta }}</router-link>
        </li>
        <li :class="{ clear: !openConcerns.length }">
          <span class="n">{{ openConcerns.length }}</span><span>open concerns</span><span></span>
        </li>
      </ul>
    </div>

    <div class="card panel">
      <h2>Matches by status <span class="muted">{{ db.matches.length }} in all</span></h2>
      <div class="donut-wrap">
        <DonutChart :parts="matchParts" :centre="db.matches.length" caption="matches" />
        <ul class="legend">
          <li v-for="p in matchParts" :key="p.label"><span class="dot" :style="{ background: p.color }"></span>{{ p.label }}<b>{{ p.value }}</b></li>
        </ul>
      </div>
    </div>
  </div>

  <div class="panels cols-3">
    <div class="card panel">
      <h2>Mentorship health <span class="muted">weekly check-ins</span></h2>
      <div class="bignum"><strong>{{ pulse.asked ? pulse.responseRate + '%' : '-' }}</strong><span>answered ({{ pulse.answered }} of {{ pulse.asked }})</span></div>
      <div class="stackbar" aria-hidden="true">
        <span v-for="r in pulseRows" :key="r.label" :style="{ width: share(r.value, pulse.asked), background: r.color }"></span>
      </div>
      <div v-for="r in pulseRows" :key="r.label" class="hbar">
        <span>{{ r.label }}</span>
        <span class="track"><span :style="{ width: share(r.value, pulse.asked), background: r.color }"></span></span>
        <b>{{ r.value }}</b>
      </div>
      <p class="muted hint" style="margin: 10px 0 0"><router-link to="/admin/pulse">Open Mentorship Pulse</router-link></p>
    </div>

    <div class="card panel">
      <h2>Mentor capacity <span class="muted">{{ capacity.used }} of {{ capacity.places }} places</span></h2>
      <div class="bignum"><strong>{{ capacity.percent }}%</strong><span>of places in use</span></div>
      <div v-for="r in capacity.rows" :key="r.id" class="hbar">
        <span>{{ userName(db, r.id) }}</span>
        <span class="track"><span :style="{ width: share(r.used, r.max), background: r.used >= r.max ? '#c0566b' : '#4f9d6b' }"></span></span>
        <b>{{ r.used }}/{{ r.max }}</b>
      </div>
      <p v-if="!capacity.rows.length" class="muted">No verified mentors yet.</p>
    </div>

    <div class="card panel">
      <h2>Student feedback <span class="muted">{{ feedback.total }} in all</span></h2>
      <div class="bignum"><strong>{{ feedback.average === null ? '-' : feedback.average }}</strong><span>average out of 5</span></div>
      <div v-for="r in feedback.counts" :key="r.rating" class="hbar">
        <span>{{ r.rating }} star{{ r.rating > 1 ? 's' : '' }}</span>
        <span class="track"><span :style="{ width: share(r.count, feedback.total), background: '#8c50ae' }"></span></span>
        <b>{{ r.count }}</b>
      </div>
    </div>
  </div>

  <div class="card panel" style="margin-bottom: 18px">
    <h2>Recommended matches</h2>
    <p class="muted hint">The best mentor for each waiting student, with a Smart Match score out of 100. <router-link to="/admin/matches">See the top 3</router-link></p>
    <RecommendationTable :per-student="1" compact />
  </div>

  <div class="panels cols-3">
    <div class="card panel">
      <h2>Open concerns <span class="muted">{{ openConcerns.length }}</span></h2>
      <ul class="feed">
        <li v-for="c in openConcerns" :key="c.id">{{ userName(db, c.raisedBy) }}: {{ c.text }}
          <div class="actions"><button class="btn small" type="button" @click="resolve(c.id)">Mark resolved</button></div></li>
        <li v-if="!openConcerns.length" class="muted">No open concerns.</li>
      </ul>
    </div>
    <div class="card panel">
      <h2>Latest feedback</h2>
      <ul class="feed">
        <li v-for="f in recentFeedback" :key="f.id"><b>{{ f.rating }}/5</b> · {{ userName(db, f.authorId) }} about {{ mentorOf(f) }}
          <span class="meta">{{ f.comments || 'No comment' }} · {{ when(f.at) }}</span></li>
        <li v-if="!recentFeedback.length" class="muted">No feedback yet.</li>
      </ul>
    </div>
    <div class="card panel">
      <h2>Recent activity</h2>
      <NotificationList :items="notes" empty="Nothing yet." />
    </div>
  </div>
</template>
