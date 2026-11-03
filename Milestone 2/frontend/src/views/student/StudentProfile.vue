<script setup>
import { reactive, ref } from 'vue';
import { FORMATS, DURATIONS } from '../../config/constants';
import { session } from '../../services/auth';
import { saveStudentProfile } from '../../services/profiles';
import { useDb } from '../../composables/useDb';
import { useToast } from '../../composables/useToast';
import PageHeading from '../../components/common/PageHeading.vue';
import TopicPicker from '../../components/common/TopicPicker.vue';

const { db, commit } = useDb();
const { toast } = useToast();
const me = session.value;
const p = db.students[me.id];
const form = reactive({
  programme: p.programme, goals: p.goals, skills: p.skills, topics: [...p.topics], format: p.format,
  duration: p.duration, availability: p.availability, preferences: p.preferences
});
const error = ref('');

function save() {
  error.value = saveStudentProfile(db, me.id, form) || '';
  if (error.value) return;
  commit();
  toast('Profile saved');
}
</script>

<template>
  <PageHeading eyebrow="Student" title="My profile" intro="The admin uses this to find you a suitable mentor. Other students and mentors cannot see it." />
  <div class="card">
    <form @submit.prevent="save">
      <label for="programme">Programme level</label>
      <input id="programme" v-model="form.programme" />
      <label for="goals">Career goals and the guidance you need (max 500 characters)</label>
      <textarea id="goals" v-model="form.goals" rows="3"></textarea>
      <label for="skills">Skills</label>
      <input id="skills" v-model="form.skills" />
      <label>Topics you would like a mentor for</label>
      <TopicPicker v-model="form.topics" />
      <label for="format">Preferred format</label>
      <select id="format" v-model="form.format"><option v-for="o in FORMATS" :key="o">{{ o }}</option></select>
      <label for="duration">Expected duration</label>
      <select id="duration" v-model="form.duration"><option v-for="o in DURATIONS" :key="o">{{ o }}</option></select>
      <label for="availability">Availability (days or time windows you are free, optional)</label>
      <input id="availability" v-model="form.availability" />
      <label for="preferences">Other mentoring preferences</label>
      <textarea id="preferences" v-model="form.preferences" rows="2"></textarea>
      <div class="err" role="alert">{{ error }}</div>
      <div class="actions"><button class="btn" type="submit">Save profile</button></div>
    </form>
  </div>
</template>
