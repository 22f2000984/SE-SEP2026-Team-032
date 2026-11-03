/* Login, registration and the signed-in user. The session lives in sessionStorage (one per browser tab). */
import { ref } from 'vue';
import { DEFAULT_CAPACITY } from '../config/constants';
import { nextId } from './ids';
import { notifyAdmins } from './notifications';

const SESSION_KEY = 't32_vue_session';

function readSession() {
  try { return JSON.parse(sessionStorage.getItem(SESSION_KEY)); } catch { return null; }
}
export const session = ref(readSession());

export function startSession(user) {
  session.value = { id: user.id, name: user.name, role: user.role };
  try { sessionStorage.setItem(SESSION_KEY, JSON.stringify(session.value)); } catch { /* storage blocked */ }
}
export function logout() {
  session.value = null;
  try { sessionStorage.removeItem(SESSION_KEY); } catch { /* storage blocked */ }
}

/* Returns the user, or null when the email or password is wrong. */
export function login(d, email, password) {
  const u = d.users.find(x => x.email === email.trim().toLowerCase() && x.password === password);
  if (u) startSession(u);
  return u || null;
}

/* Returns an error message, or null when the account was created. */
export function register(d, { role, name, email, password }) {
  const n = name.trim(), e = email.trim().toLowerCase();
  if (!n) return 'Enter your name.';
  if (!/^\S+@\S+\.\S+$/.test(e)) return 'Enter a valid email.';
  if (password.length < 6) return 'Password needs at least 6 characters.';
  if (d.users.some(u => u.email === e)) return 'This email is already registered.';
  const id = nextId(d);
  d.users.push({ id, email: e, password, name: n, role });
  if (role === 'student') {
    d.students[id] = { programme: '', goals: '', skills: '', topics: [], format: 'No preference', duration: 'Not sure yet', preferences: '', availability: '' };
  } else {
    d.mentors[id] = { qualifications: '', experience: 0, topics: [], bio: '', status: 'pending', maxStudents: DEFAULT_CAPACITY };
  }
  notifyAdmins(d, `New ${role} registered: ${n}.`);
  return null;
}
