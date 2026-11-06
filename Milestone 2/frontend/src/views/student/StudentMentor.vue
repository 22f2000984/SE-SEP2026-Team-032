<script setup>
import { computed, ref } from 'vue';
import { NEXT_STEP } from '../../config/constants';
import { session } from '../../services/auth';
import { respond } from '../../services/matches';
import { addFeedback, addConcern } from '../../services/feedback';
import { useDb } from '../../composables/useDb';
import { useToast } from '../../composables/useToast';
import { latestMatchOf, userName, topicsText, when } from '../../utils/format';
import PageHeading from '../../components/common/PageHeading.vue';
import StatusPill from '../../components/common/StatusPill.vue';

const { db, commit } = useDb();
const { toast } = useToast();
const me = session.value;

const match = computed(() => latestMatchOf(db, me.id));
const shown = computed(() => match.value && ['proposed', 'active', 'completed'].includes(match.value.status));
const live = computed(() => match.value && ['active', 'completed'].includes(match.value.status));
const mentor = computed(() => (shown.value ? db.mentors[match.value.mentorId] : null));
const myFeedback = computed(() => (match.value ? db.feedback.filter(f => f.matchId === match.value.id && f.authorId === me.id) : []));
const myConcerns = computed(() => db.concerns.filter(c => c.raisedBy === me.id));

const rating = ref(5);
const comments = ref('');
const concern = ref('');
const concernError = ref('');

function answer(value) {
  respond(db, match.value, 'student', value);
  commit();
  toast(value === 'accepted' ? 'You accepted the proposal' : 'You declined the proposal');
}
function sendFeedback() {
  addFeedback(db, match.value.id, me.id, rating.value, comments.value);
  commit();
  comments.value = '';
  toast('Thank you for your feedback');
}
function sendConcern() {
  concernError.value = addConcern(db, match.value.id, me.id, concern.value) || '';
  if (concernError.value) return;
  commit();
  concern.value = '';
  toast('Concern sent to the admin');
}
</script>

<template>
  <PageHeading eyebrow="Student" title="My mentor" />
  <div v-if="match" class="info"><b>Status:</b> <StatusPill :value="match.status" /> &nbsp; <b>Next step:</b> {{ NEXT_STEP[match.status] }}</div>

  <template v-if="!shown">
    <div class="info">{{ match ? 'Your last match was cancelled. The admin will arrange a new one.' : 'No mentor proposed yet. The admin will arrange one after reviewing your profile.' }}</div>
    <p class="muted">You cannot browse mentors. The admin chooses the match for you.</p>
  </template>

  <div v-else class="stack">
    <div class="card">
      <h2>{{ userName(db, match.mentorId) }} <StatusPill v-if="live" :value="match.status" /></h2>
      <p v-if="live"><b>Email:</b> {{ db.users.find(u => u.id === match.mentorId).email }} (also sent to you by email). Write to your mentor to agree session times and how you will talk.</p>
      <p><b>Qualifications:</b> {{ mentor.qualifications }}<br /><b>Topics:</b> {{ topicsText(mentor.topics) }}<br /><b>Experience:</b> {{ mentor.experience }} years</p>
      <p>{{ mentor.bio }}</p>
    </div>

    <div v-if="match.status === 'proposed'" class="card">
      <h2>Do you accept this mentor?</h2>
      <p>
        Mentor's response: <StatusPill :value="match.mentorResponse" /> &nbsp; Your response: <StatusPill :value="match.studentResponse" />
        <span v-if="match.studentRespondedAt" class="muted"> recorded {{ when(match.studentRespondedAt) }}</span>
      </p>
      <div v-if="match.studentResponse === 'pending'" class="actions">
        <button class="btn" type="button" @click="answer('accepted')">Accept</button>
        <button class="btn danger" type="button" @click="answer('declined')">Decline</button>
      </div>
      <p v-else class="muted">The admin confirms the match once both of you have accepted.</p>
    </div>

    <div v-if="live" class="card">
      <h2>Give feedback</h2>
      <p v-for="f in myFeedback" :key="f.id" class="muted">You rated this match {{ f.rating }}/5 on {{ when(f.at) }}.</p>
      <form @submit.prevent="sendFeedback">
        <label for="rating">Rating</label>
        <select id="rating" v-model="rating"><option v-for="n in [5, 4, 3, 2, 1]" :key="n" :value="n">{{ n }}</option></select>
        <label for="comments">Comments</label>
        <textarea id="comments" v-model="comments" rows="3"></textarea>
        <div class="actions"><button class="btn" type="submit">Send feedback</button></div>
      </form>
    </div>
  </div>

  <div v-if="match" class="card" style="margin-top: 16px">
    <h2>Raise a concern</h2>
    <p class="muted">Use this if the match is not working. The admin will review it.</p>
    <form @submit.prevent="sendConcern">
      <label class="sr-only" for="concern">Your concern</label>
      <textarea id="concern" v-model="concern" rows="3"></textarea>
      <div class="err" role="alert">{{ concernError }}</div>
      <div class="actions"><button class="btn danger" type="submit">Submit concern</button></div>
    </form>
    <ul class="list"><li v-for="c in myConcerns" :key="c.id">{{ c.text }} <StatusPill :value="c.status" /></li></ul>
  </div>
</template>
