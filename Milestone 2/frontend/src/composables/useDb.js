import { db, commit } from '../services/db';

/* Views use this to read the data and to save after a change. */
export function useDb() {
  return { db, commit };
}
