<script setup>
import { computed, ref } from 'vue';
import { session } from '../../services/auth';
import { loadQuiz, sendQuiz } from '../../services/remote';
import { useDb } from '../../composables/useDb';
import { useToast } from '../../composables/useToast';

/* "Not sure of your level?" A short quiz for one of the student's topics. Needs the backend. */
const { db } = useDb();
const { toast } = useToast();
const me = session.value;

const profile = computed(() => db.students[me.id]);
const topic = ref('');
const questions = ref([]);
const answers = ref([]);
const error = ref('');

async function start() {
  error.value = '';
  const result = await loadQuiz();
  if (result.error) { error.value = result.error; return; }
  questions.value = result.questions;
  answers.value = result.questions.map(() => null);
}
async function submit() {
  if (answers.value.includes(null)) { error.value = 'Answer every question.'; return; }
  error.value = (await sendQuiz(topic.value, answers.value)) || '';
  if (error.value) return;
  questions.value = [];
  toast('Your level is saved');
}
</script>

<template>
  <div class="card">
    <h2>Not sure of your level?</h2>
    <p class="muted">Take a short quiz for a topic. The admin sees the level when choosing a mentor.</p>
    <ul v-if="Object.keys(profile.levels || {}).length" class="list">
      <li v-for="(level, name) in profile.levels" :key="name"><b>{{ name }}:</b> {{ level }}</li>
    </ul>
    <p v-if="!profile.topics.length" class="muted">Add a topic to your profile first.</p>
    <form v-else @submit.prevent="questions.length ? submit() : start()">
      <label for="quiz-topic">Topic</label>
      <select id="quiz-topic" v-model="topic" required>
        <option value="" disabled>Choose…</option>
        <option v-for="t in profile.topics" :key="t">{{ t }}</option>
      </select>
      <template v-for="(q, i) in questions" :key="q.question">
        <label :for="'quiz' + i">{{ q.question }}</label>
        <select :id="'quiz' + i" v-model="answers[i]">
          <option :value="null" disabled>Choose…</option>
          <option v-for="(option, n) in q.options" :key="option" :value="n">{{ option }}</option>
        </select>
      </template>
      <div class="err" role="alert">{{ error }}</div>
      <div class="actions"><button class="btn" type="submit">{{ questions.length ? 'Get my level' : 'Take the quiz' }}</button></div>
    </form>
  </div>
</template>
