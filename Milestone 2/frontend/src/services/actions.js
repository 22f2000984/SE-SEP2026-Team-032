/* The one place the pages call to change data. With the backend on (VITE_API_URL) each action calls the API;
   otherwise it uses the browser sample data. Every action is async and returns an error message (or null), so the
   pages work the same in both modes. */
import { API_ON } from './api';
import { db } from './db';
import * as local from './auth';
import * as profiles from './profiles';
import * as matches from './matches';
import * as feedback from './feedback';
import { submitCheckIn as submitLocalCheckIn, markReviewed as markLocalReviewed } from './checkins';
import * as remote from './remote';
import { hasOpenMatch } from './matching';

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

/* Student: ask for a mentor, or say you do not need one now. */
export async function setLooking(studentId, looking) {
  if (API_ON) return remote.setLooking(studentId, looking);
  if (hasOpenMatch(db, studentId)) return looking ? 'You already have a mentor match.' : 'You have an open match. Ask the admin to cancel it first.';
  db.students[studentId].looking = looking;
  return null;
}

/* Feedback and concerns about a match (browser sample data without the backend). */
export async function sendFeedback(matchId, authorId, rating, comments) {
  if (API_ON) return remote.sendFeedback(matchId, authorId, rating, comments);
  feedback.addFeedback(db, matchId, authorId, rating, comments);
  return null;
}
export async function sendConcern(matchId, userId, text) { return API_ON ? remote.sendConcern(matchId, userId, text) : feedback.addConcern(db, matchId, userId, text); }
export async function resolveConcern(id) {
  if (API_ON) return remote.resolveConcern(id);
  feedback.resolveConcern(db, id);
  return null;
}

/* A student or mentor answers their weekly check-in. Returns an error message, or null when it was saved. */
export async function submitCheckIn(id, form) { return API_ON ? remote.submitCheckIn(id, form) : submitLocalCheckIn(db, id, form); }

/* The admin marks a flagged check-in as reviewed, with an optional note. Returns an error message, or null. */
export async function markReviewed(id, note) {
  if (API_ON) return remote.markReviewed(id, note);
  markLocalReviewed(db, id, note);
  return null;
}
