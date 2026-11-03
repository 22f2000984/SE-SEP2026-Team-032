<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { HOME } from '../../config/constants';
import { login, logout } from '../../services/auth';
import { resetDb } from '../../services/db';
import { useDb } from '../../composables/useDb';
import { useToast } from '../../composables/useToast';

const router = useRouter();
const { db } = useDb();
const { toast } = useToast();
const email = ref('');
const password = ref('');
const error = ref('');

function submit() {
  if (!email.value.trim() || !password.value) { error.value = 'Enter your email and password.'; return; }
  const user = login(db, email.value, password.value);
  if (!user) { error.value = 'Wrong email or password.'; return; }
  router.push(HOME[user.role]);
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
      <button class="btn" type="submit">Log in</button>
    </form>
    <div class="info"><b>Demo accounts</b> (password <code>demo123</code>)<br />asha@student.test · meera@mentor.test · admin@client.test</div>
    <p class="muted">Students and mentors cannot browse each other. The admin arranges every match.</p>
    <p><a href="#" class="muted" @click.prevent="reset">Reset demo data</a></p>
  </main>
</template>
