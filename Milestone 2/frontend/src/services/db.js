/* The data layer. Today it keeps one reactive object in the browser (localStorage).
   In Sprint 1 these functions become calls to the backend APIs; the views do not change. */
import { reactive } from 'vue';
import { createSeed } from '../data/seed';

const KEY = 't32_vue_db_v2';

function read() {
  try {
    const d = JSON.parse(localStorage.getItem(KEY));
    if (d && d.users) return d;
  } catch { /* fall through to the sample data */ }
  return null;
}

export const db = reactive(read() || createSeed());

/* Save after every change. */
export function commit() {
  try { localStorage.setItem(KEY, JSON.stringify(db)); } catch { /* storage blocked */ }
}
export function resetDb() {
  Object.keys(db).forEach(k => delete db[k]);
  Object.assign(db, createSeed());
  commit();
}
commit();
