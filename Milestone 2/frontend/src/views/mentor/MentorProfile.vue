<script setup>
import { computed, reactive, ref } from 'vue';
import { WEEKDAYS, MAX_CAPACITY } from '../../config/constants';
import { session } from '../../services/auth';
import { saveMentorProfile, addSlot, removeSlot } from '../../services/profiles';
import { useDb } from '../../composables/useDb';
import { useToast } from '../../composables/useToast';
import PageHeading from '../../components/common/PageHeading.vue';
import StatusPill from '../../components/common/StatusPill.vue';
import TopicPicker from '../../components/common/TopicPicker.vue';
import CapacityBar from '../../components/common/CapacityBar.vue';

const { db, commit } = useDb();
const { toast } = useToast();
const me = session.value;
const p = db.mentors[me.id];

const form = reactive({ qualifications: p.qualifications, experience: p.experience, topics: [...p.topics], maxStudents: p.maxStudents, bio: p.bio, skillsText: p.skillsText || '' });
const error = ref('');
const slot = reactive({ day: 'Monday', start: '18:00', end: '19:00' });
const slotError = ref('');
const slots = computed(() => db.slots.filter(s => s.mentorId === me.id));

function save() {
  error.value = saveMentorProfile(db, me.id, form) || '';
  if (error.value) return;
  commit();
  toast('Profile saved');
}
function add() {
  slotError.value = addSlot(db, me.id, slot.day, slot.start, slot.end) || '';
  if (slotError.value) return;
  commit();
  toast('Slot added');
}
function remove(id) {
  removeSlot(db, id);
  commit();
}
</script>

<template>
  <PageHeading eyebrow="Mentor" title="My profile">
    <template #badge> <StatusPill :value="p.status" /></template>
  </PageHeading>
  <div class="row">
    <div class="card">
      <h2>Background</h2>
      <form novalidate @submit.prevent="save">
        <label for="qualifications">Qualifications</label>
        <input id="qualifications" v-model="form.qualifications" />
        <label for="experience">Years of experience</label>
        <input id="experience" v-model="form.experience" type="number" min="0" max="60" />
        <label>Topics you can mentor</label>
        <TopicPicker v-model="form.topics" />
        <label for="max">Maximum students you can mentor at the same time (1 to {{ MAX_CAPACITY }})</label>
        <input id="max" v-model="form.maxStudents" type="number" min="1" :max="MAX_CAPACITY" />
        <p class="muted"><CapacityBar :mentor-id="me.id" /></p>
        <label for="offer">What you can offer as a mentor, in your own words (max 800 characters)</label>
        <textarea id="offer" v-model="form.skillsText" rows="4" placeholder="For example: I coach students on product careers, requirements writing and mock interviews."></textarea>
        <p class="muted">Smart Match reads this to find students who fit. Please do not write phone numbers or addresses.</p>
        <label for="bio">Short bio</label>
        <textarea id="bio" v-model="form.bio" rows="4"></textarea>
        <div class="err" role="alert">{{ error }}</div>
        <div class="actions"><button class="btn" type="submit">Save profile</button></div>
      </form>
    </div>

    <div class="card">
      <h2>Availability</h2>
      <ul class="list">
        <li v-for="s in slots" :key="s.id">{{ s.day }} {{ s.start }} to {{ s.end }} <button class="btn small ghost" type="button" @click="remove(s.id)">Remove</button></li>
        <li v-if="!slots.length" class="muted">No slots yet.</li>
      </ul>
      <form @submit.prevent="add">
        <label for="day">Day</label>
        <select id="day" v-model="slot.day"><option v-for="d in WEEKDAYS" :key="d">{{ d }}</option></select>
        <div class="row">
          <div><label for="start">From</label><input id="start" v-model="slot.start" type="time" /></div>
          <div><label for="end">To</label><input id="end" v-model="slot.end" type="time" /></div>
        </div>
        <div class="err" role="alert">{{ slotError }}</div>
        <div class="actions"><button class="btn" type="submit">Add slot</button></div>
      </form>
    </div>
  </div>
</template>
