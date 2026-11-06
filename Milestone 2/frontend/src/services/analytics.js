/* Numbers for the admin overview: everything is counted from the data, nothing is stored separately. */
import { STATUSES } from '../config/constants';
import { used, maxOf, waitingStudents } from './matching';
import { stateOf } from './checkins';

const pct = (a, b) => (b ? Math.round((a / b) * 100) : 0);

export function matchCounts(d) {
  return STATUSES.map(status => ({ status, count: d.matches.filter(m => m.status === status).length }));
}

/* How the weekly check-ins of active matches are going. Only check-ins that are due or older count. */
export function pulseSummary(d, now = Date.now()) {
  const live = d.checkins.filter(c => d.matches.some(m => m.id === c.matchId && m.status === 'active') && stateOf(c, now) !== 'upcoming');
  const answered = live.filter(c => c.submittedAt);
  const verdict = v => answered.filter(c => c.review && c.review.verdict === v).length;
  return {
    asked: live.length,
    answered: answered.length,
    responseRate: pct(answered.length, live.length),
    onTrack: verdict('on track'),
    watch: verdict('watch'),
    needsAttention: verdict('needs attention'),
    unanswered: live.length - answered.length
  };
}

export function feedbackSummary(d) {
  const counts = [5, 4, 3, 2, 1].map(r => ({ rating: r, count: d.feedback.filter(f => f.rating === r).length }));
  const total = d.feedback.length;
  const average = total ? d.feedback.reduce((s, f) => s + f.rating, 0) / total : null;
  return { total, average: average === null ? null : Math.round(average * 10) / 10, counts };
}

/* Places in use across all verified mentors, and one line per mentor. */
export function capacitySummary(d) {
  const mentors = Object.keys(d.mentors).map(Number).filter(id => d.mentors[id].status === 'verified');
  const rows = mentors.map(id => ({ id, used: used(d, id), max: maxOf(d, id) }));
  const taken = rows.reduce((s, r) => s + r.used, 0), places = rows.reduce((s, r) => s + r.max, 0);
  return { rows, used: taken, places, percent: pct(taken, places) };
}

export function peopleSummary(d) {
  const mentors = Object.values(d.mentors);
  return {
    students: d.users.filter(u => u.role === 'student').length,
    waiting: waitingStudents(d).length,
    mentors: mentors.length,
    verified: mentors.filter(m => m.status === 'verified').length,
    pending: mentors.filter(m => m.status === 'pending').length
  };
}
