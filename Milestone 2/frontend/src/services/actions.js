/* The one place the pages call to change data. With the backend on (VITE_API_URL) each action calls the API;
   otherwise it uses the browser sample data. Every action is async and returns an error message (or null), so the
   pages work the same in both modes. */
import { API_ON } from './api';
import { db } from './db';
import * as local from './auth';
import * as profiles from './profiles';
import * as matches from './matches';
import * as remote from './remote';

export async function login(email, password) {
  if (API_ON) return remote.login(email, password);
  const user = local.login(db, email, password);
  return user ? { user } : { error: 'Wrong email or password.' };
}
export async function register(form) { return API_ON ? remote.register(form) : local.register(db, form); }

export async function saveStudentProfile(id, form) { return API_ON ? remote.saveStudentProfile(id, form) : profiles.saveStudentProfile(db, id, form); }
export async function saveMentorProfile(id, form) { return API_ON ? remote.saveMentorProfile(id, form) : profiles.saveMentorProfile(db, id, form); }
export async function adminEditMentor(id, form) { return API_ON ? remote.adminEditMentor(id, form) : profiles.adminEditMentor(db, id, form); }
export async function verifyMentor(id) {
  if (API_ON) return remote.verifyMentor(id);
  profiles.verifyMentor(db, id);
  return null;
}
export async function addSlot(id, day, start, end) { return API_ON ? remote.addSlot(id, day, start, end) : profiles.addSlot(db, id, day, start, end); }
export async function removeSlot(slotId) {
  if (API_ON) return remote.removeSlot(slotId);
  profiles.removeSlot(db, slotId);
  return null;
}

export async function proposeMatch(studentId, mentorId, notes, by) {
  return API_ON ? remote.proposeMatch(studentId, mentorId, notes) : matches.proposeMatch(db, studentId, mentorId, notes, by);
}
export async function respond(match, who, answer) {
  if (API_ON) return remote.respond(match, who, answer);
  matches.respond(db, match, who, answer);
  return null;
}
/* Returns an error message, or null when the status changed. */
export async function setStatus(match, to, by) {
  if (API_ON) return remote.setStatus(match, to);
  return matches.setStatus(db, match, to, by) ? null : 'Both the mentor and the student must accept first.';
}
