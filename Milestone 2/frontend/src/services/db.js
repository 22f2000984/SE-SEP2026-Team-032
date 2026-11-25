/* The data layer. Today it keeps one reactive object in the browser (localStorage).
   In Sprint 1 these functions become calls to the backend APIs; the views do not change. */
import { reactive } from 'vue';
import { createSeed } from '../data/seed';
import { API_ON } from './api';

const KEY = 't32_vue_db_v2';

function read() {
  try {
    const d = JSON.parse(localStorage.getItem(KEY));
    if (d && d.users) return d;
  } catch { /* fall through to the sample data */ }
  return null;
}

/* With the backend on, db starts empty and is filled from the API after login (see remote.js). */
const empty = () => ({ nextId: 100, users: [], students: {}, mentors: {}, slots: [], matches: [], checkins: [], concerns: [], feedback: [], notifications: [], emails: [] });
export const db = reactive(API_ON ? empty() : read() || createSeed());

/* Save after every change. */
export function commit() {
  if (API_ON) return; // the backend keeps the data
  try { localStorage.setItem(KEY, JSON.stringify(db)); } catch { /* storage blocked */ }
}
export function resetDb() {
  Object.keys(db).forEach(k => delete db[k]);
  Object.assign(db, createSeed());
  commit();
}
commit();
