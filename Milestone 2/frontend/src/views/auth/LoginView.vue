<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { HOME } from '../../config/constants';
import { logout } from '../../services/auth';
import { login } from '../../services/actions';
import { API_ON } from '../../services/api';
import { resetDb } from '../../services/db';
import { useToast } from '../../composables/useToast';

const router = useRouter();
const { toast } = useToast();
const api = API_ON;
const email = ref('');
const password = ref('');
const error = ref('');
const busy = ref(false);

async function submit() {
  if (!email.value.trim() || !password.value) { error.value = 'Enter your email and password.'; return; }
  busy.value = true;
  error.value = '';
  const result = await login(email.value, password.value);
  busy.value = false;
  if (result.error) { error.value = result.error; return; }
  router.push(HOME[result.user.role]);
}
function reset() {
  resetDb();
  logout();
  toast('Demo data has been reset');
}
</script>

<template>
  <nav class="auth-top"><span>New to Mentor Connect?</span><router-link to="/register">Create an Account</router-link></nav>
  <main class="auth-form">
    <div class="eyebrow">Welcome back</div>
    <h1>Log in</h1>
    <p class="intro">Student Mentoring and Career Support</p>
    <form novalidate @submit.prevent="submit">
      <label for="email">Email</label>
      <input id="email" v-model="email" type="email" autocomplete="username" />
      <label for="pw">Password</label>
      <input id="pw" v-model="password" type="password" autocomplete="current-password" />
      <div class="err" role="alert">{{ error }}</div>
      <button class="btn" type="submit" :disabled="busy">{{ busy ? 'Logging in…' : 'Log in' }}</button>
      <p v-if="busy && api" class="muted">The server may need up to a minute to wake up the first time.</p>
    </form>
    <div class="info"><b>Demo accounts</b> (password <code>demo123</code>)<br />{{ api ? 'asha@ds.study.iitm.ac.in · meera@mentor.test · admin@client.test' : 'asha@student.test · meera@mentor.test · admin@client.test' }}</div>
    <p class="muted">Students and mentors cannot browse each other. The admin arranges every match.</p>
    <p v-if="!api"><a href="#" class="muted" @click.prevent="reset">Reset demo data</a></p>
  </main>
</template>
