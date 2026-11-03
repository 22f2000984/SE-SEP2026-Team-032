/* Matching rules. Pure functions: they read the data and return results, they never change it. */
import { WEIGHTS, DEFAULT_CAPACITY, EXPERIENCE_CAP_YEARS } from '../config/constants';

/* Places a mentor has taken: proposed and active matches both count. */
export function used(d, mentorId) {
  return d.matches.filter(m => m.mentorId === mentorId && ['proposed', 'active'].includes(m.status)).length;
}
export function maxOf(d, mentorId) {
  return d.mentors[mentorId].maxStudents || DEFAULT_CAPACITY;
}
export function hasOpenMatch(d, studentId) {
  return d.matches.some(m => m.studentId === studentId && ['proposed', 'active'].includes(m.status));
}

/* Returns null when the pair may be proposed, otherwise the reason it may not. */
export function eligible(d, studentId, mentorId) {
  if (!d.mentors[mentorId] || d.mentors[mentorId].status !== 'verified') return 'The mentor is not verified yet.';
  if (used(d, mentorId) >= maxOf(d, mentorId)) return 'This mentor has no free places.';
  if (hasOpenMatch(d, studentId)) return 'This student already has an open match.';
  return null;
}

/* Score out of 100: topics 70 (share of the student's wanted topics the mentor covers) and
   experience 30 (years, up to 10). Free places give no points; they only decide eligibility. */
export function scoreMatch(d, studentId, mentorId) {
  const s = d.students[studentId], m = d.mentors[mentorId], reasons = [];
  const shared = (s.topics || []).filter(t => (m.topics || []).includes(t));
  const topics = s.topics && s.topics.length ? Math.round(WEIGHTS.topics * shared.length / s.topics.length) : 0;
  reasons.push(shared.length ? `Shared topics: ${shared.join(', ')}` : 'No shared topics');
  const years = m.experience || 0;
  const experience = Math.round(WEIGHTS.experience * Math.min(years, EXPERIENCE_CAP_YEARS) / EXPERIENCE_CAP_YEARS);
  reasons.push(`${years} years of experience`);
  const free = Math.max(0, maxOf(d, mentorId) - used(d, mentorId));
  reasons.push(`${free} of ${maxOf(d, mentorId)} places free`);
  return { total: topics + experience, parts: { topics, experience }, reasons };
}

/* Best eligible mentors for one student, highest score first. */
export function recommend(d, studentId, n) {
  return Object.keys(d.mentors).map(Number)
    .filter(mentorId => !eligible(d, studentId, mentorId))
    .map(mentorId => ({ mentorId, ...scoreMatch(d, studentId, mentorId) }))
    .sort((a, b) => b.total - a.total)
    .slice(0, n);
}

export function waitingStudents(d) {
  return d.users.filter(u => u.role === 'student' && !hasOpenMatch(d, u.id));
}
