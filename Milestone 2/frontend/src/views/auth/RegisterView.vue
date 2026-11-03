<script setup>
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { register } from '../../services/auth';
import { useDb } from '../../composables/useDb';
import { useToast } from '../../composables/useToast';

const router = useRouter();
const { db, commit } = useDb();
const { toast } = useToast();
const form = reactive({ role: 'student', name: '', email: '', password: '' });
const error = ref('');

function submit() {
  error.value = register(db, form) || '';
  if (error.value) return;
  commit();
  toast('Account created. You can log in now.');
  router.push('/login');
}
</script>

<template>
  <nav class="auth-top"><span>Already have an account?</span><router-link to="/login">Sign In</router-link></nav>
  <main class="auth-form">
    <div class="eyebrow">New account</div>
    <h1>Register</h1>
    <form novalidate @submit.prevent="submit">
      <label for="role">I am a</label>
      <select id="role" v-model="form.role"><option value="student">Student</option><option value="mentor">Mentor</option></select>
      <label for="name">Full name</label>
      <input id="name" v-model="form.name" />
      <label for="email">Email</label>
      <input id="email" v-model="form.email" type="email" />
      <label for="pw">Password (min 6 characters)</label>
      <input id="pw" v-model="form.password" type="password" autocomplete="new-password" />
      <div class="err" role="alert">{{ error }}</div>
      <button class="btn" type="submit">Create account</button>
    </form>
    <p class="muted">Mentor profiles stay pending until the admin verifies them.</p>
  </main>
</template>
