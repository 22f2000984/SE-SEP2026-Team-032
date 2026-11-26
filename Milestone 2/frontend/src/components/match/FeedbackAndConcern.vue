<script setup>
import { computed, ref } from 'vue';
import { session } from '../../services/auth';
import { sendFeedback, sendConcern } from '../../services/actions';
import { useDb } from '../../composables/useDb';
import { useToast } from '../../composables/useToast';
import { when } from '../../utils/format';
import StatusPill from '../common/StatusPill.vue';

/* Feedback and a concern about one match, written by the person who is logged in. Only the admin reads them. */
const props = defineProps({ matchId: { type: Number, required: true } });
const { db, commit } = useDb();
const { toast } = useToast();
const me = session.value;

const myFeedback = computed(() => db.feedback.find(f => f.matchId === props.matchId && f.authorId === me.id));
const myConcerns = computed(() => db.concerns.filter(c => c.matchId === props.matchId && c.raisedBy === me.id));

const rating = ref(5);
const comments = ref('');
const concern = ref('');
const feedbackError = ref('');
const concernError = ref('');

async function giveFeedback() {
  feedbackError.value = (await sendFeedback(props.matchId, me.id, rating.value, comments.value)) || '';
  if (feedbackError.value) return;
  commit();
  comments.value = '';
  toast('Thank you for your feedback');
}
async function raiseConcern() {
  concernError.value = (await sendConcern(props.matchId, me.id, concern.value)) || '';
  if (concernError.value) return;
  commit();
  concern.value = '';
  toast('Concern sent to the admin');
}
</script>

<template>
  <details>
    <summary>Feedback and concerns</summary>

    <p v-if="myFeedback" class="muted">You rated this match {{ myFeedback.rating }}/5 on {{ when(myFeedback.at) }}.</p>
    <form v-else @submit.prevent="giveFeedback">
      <label :for="'rating' + matchId">Rating (5 is best)</label>
      <select :id="'rating' + matchId" v-model="rating"><option v-for="n in [5, 4, 3, 2, 1]" :key="n" :value="n">{{ n }}</option></select>
      <label :for="'comments' + matchId">Comments</label>
      <textarea :id="'comments' + matchId" v-model="comments" rows="2"></textarea>
      <div class="err" role="alert">{{ feedbackError }}</div>
      <div class="actions"><button class="btn small" type="submit">Send feedback</button></div>
    </form>

    <form @submit.prevent="raiseConcern">
      <label :for="'concern' + matchId">Raise a concern</label>
      <textarea :id="'concern' + matchId" v-model="concern" rows="2"></textarea>
      <div class="err" role="alert">{{ concernError }}</div>
      <div class="actions"><button class="btn small danger" type="submit">Submit concern</button></div>
    </form>
    <ul class="list"><li v-for="c in myConcerns" :key="c.id">{{ c.text }} <StatusPill :value="c.status" /></li></ul>
  </details>
</template>
