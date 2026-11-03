<script setup>
import { computed, reactive, ref } from 'vue';
import { MAX_CAPACITY } from '../../config/constants';
import { adminEditMentor, verifyMentor, slotText } from '../../services/profiles';
import { useDb } from '../../composables/useDb';
import { useToast } from '../../composables/useToast';
import { userName } from '../../utils/format';
import PageHeading from '../../components/common/PageHeading.vue';
import StatusPill from '../../components/common/StatusPill.vue';
import TopicChips from '../../components/common/TopicChips.vue';
import TopicPicker from '../../components/common/TopicPicker.vue';
import CapacityBar from '../../components/common/CapacityBar.vue';

const { db, commit } = useDb();
const { toast } = useToast();
const q = ref('');
const editing = ref(null);
const form = reactive({ qualifications: '', experience: 0, topics: [], maxStudents: 3, bio: '' });
const error = ref('');

const mentorIds = computed(() => Object.keys(db.mentors).map(Number).filter(id => {
  const m = db.mentors[id];
  return !q.value || [userName(db, id), m.qualifications, m.topics.join(' '), m.bio].join(' ').toLowerCase().includes(q.value.toLowerCase());
}));

function edit(id) {
  const m = db.mentors[id];
  Object.assign(form, { qualifications: m.qualifications, experience: m.experience, topics: [...m.topics], maxStudents: m.maxStudents, bio: m.bio });
  error.value = '';
  editing.value = id;
}
function save() {
  error.value = adminEditMentor(db, editing.value, form) || '';
  if (error.value) return;
  commit();
  editing.value = null;
  toast('Mentor profile updated');
}
function verify(id) {
  verifyMentor(db, id);
  commit();
  toast('Mentor verified');
}
</script>

<template>
  <PageHeading eyebrow="Admin" title="Mentors" intro="Review mentor profiles, correct them if needed, and verify them before they can receive matches." />
  <div class="card"><label for="q">Search name, qualification or topic</label><input id="q" v-model="q" placeholder="e.g. data" /></div>

  <div class="table-wrap" style="margin-top: 16px">
    <table>
      <thead><tr><th>Mentor</th><th>Background</th><th>Availability and capacity</th><th>Status</th><th></th></tr></thead>
      <tbody>
        <template v-for="id in mentorIds" :key="id">
          <tr v-if="editing === id">
            <td colspan="5">
              <form novalidate @submit.prevent="save">
                <b>Edit {{ userName(db, id) }}</b>
                <div class="row">
                  <div><label for="qual">Qualifications</label><input id="qual" v-model="form.qualifications" /></div>
                  <div><label for="exp">Years of experience</label><input id="exp" v-model="form.experience" type="number" min="0" max="60" /></div>
                </div>
                <label>Topics</label>
                <TopicPicker v-model="form.topics" />
                <div class="row">
                  <div><label for="mx">Maximum students (1 to {{ MAX_CAPACITY }})</label><input id="mx" v-model="form.maxStudents" type="number" min="1" :max="MAX_CAPACITY" /></div>
                  <div><label for="bio">Short bio</label><input id="bio" v-model="form.bio" /></div>
                </div>
                <div class="err" role="alert">{{ error }}</div>
                <div class="actions"><button class="btn small" type="submit">Save changes</button><button class="btn small ghost" type="button" @click="editing = null">Cancel</button></div>
              </form>
            </td>
          </tr>
          <tr v-else>
            <td><b>{{ userName(db, id) }}</b></td>
            <td>{{ db.mentors[id].qualifications || '-' }} · {{ db.mentors[id].experience }} yrs<br /><TopicChips :topics="db.mentors[id].topics" /><br /><span class="muted">{{ db.mentors[id].bio }}</span></td>
            <td>{{ slotText(db, id) }}<br /><CapacityBar :mentor-id="id" /></td>
            <td><StatusPill :value="db.mentors[id].status" /></td>
            <td>
              <div class="actions">
                <button class="btn small ghost" type="button" @click="edit(id)">Edit</button>
                <button v-if="db.mentors[id].status !== 'verified'" class="btn small" type="button" @click="verify(id)">Verify</button>
              </div>
            </td>
          </tr>
        </template>
        <tr v-if="!mentorIds.length"><td colspan="5" class="muted">No mentors match.</td></tr>
      </tbody>
    </table>
  </div>
</template>
