/* Mentorship Pulse: a check-in every week for each side of an active match, reminder emails, the review of each answer,
   and what the admin has still to look at. In Sprint 1 a scheduled job creates the rows and sends the emails. */
import { CHECKIN_WEEKS, CHECKIN_GRACE_DAYS } from '../config/constants';
import { userName } from '../utils/format';
import { nextId } from './ids';
import { notifyAdmins, sendEmail } from './notifications';
import { reviewCheckIn } from './pulseReview';

const DAY = 864e5;

export function weeksFor(duration) {
  return CHECKIN_WEEKS[duration] || CHECKIN_WEEKS['Not sure yet'];
}

/* Called when a match becomes active: one row per week for the student and one for the mentor. */
export function scheduleCheckIns(d, match) {
  const start = new Date(match.confirmedAt).getTime();
  const weeks = weeksFor((d.students[match.studentId] || {}).duration);
  for (let week = 1; week <= weeks; week++) {
    ['student', 'mentor'].forEach(by => d.checkins.push({
      id: nextId(d), matchId: match.id, week, by, dueAt: new Date(start + week * 7 * DAY).toISOString(),
      submittedAt: null, rating: null, comment: '', reminderSentAt: null, review: null
    }));
  }
}

/* upcoming, due, overdue or submitted. */
export function stateOf(c, now = Date.now()) {
  if (c.submittedAt) return 'submitted';
  const due = new Date(c.dueAt).getTime();
  if (now < due) return 'upcoming';
  return now > due + CHECKIN_GRACE_DAYS * DAY ? 'overdue' : 'due';
}

export function checkInsOf(d, matchId, by) {
  return d.checkins.filter(c => c.matchId === matchId && (!by || c.by === by));
}
const activeMatch = (d, id) => d.matches.some(m => m.id === id && m.status === 'active');

/* The check-ins this person still has to answer. */
export function toAnswer(d, userId, by, now = Date.now()) {
  return d.checkins.filter(c => c.by === by && activeMatch(d, c.matchId) && ['due', 'overdue'].includes(stateOf(c, now)) &&
    d.matches.find(m => m.id === c.matchId)[by + 'Id'] === userId);
}

/* Saves an answer and runs the review. Returns an error message or null. */
export function submitCheckIn(d, id, f) {
  const c = d.checkins.find(x => x.id === id);
  const rating = Number(f.rating);
  if (!(rating >= 1 && rating <= 5)) return 'Choose a rating from 1 to 5.';
  Object.assign(c, { rating, comment: (f.comment || '').trim(), submittedAt: new Date().toISOString() });
  c.review = reviewCheckIn(c);
  if (c.review.status === 'open') {
    const m = d.matches.find(x => x.id === c.matchId);
    notifyAdmins(d, `Mentorship Pulse: week ${c.week} check-in from ${userName(d, m[c.by + 'Id'])} is marked "${c.review.verdict}". Please review.`);
  }
  return null;
}

/* Sends the reminder email for every check-in that has become due. Returns how many were sent. */
export function sendReminders(d, now = Date.now()) {
  let sent = 0;
  d.checkins.forEach(c => {
    if (c.reminderSentAt || !activeMatch(d, c.matchId) || !['due', 'overdue'].includes(stateOf(c, now))) return;
    const m = d.matches.find(x => x.id === c.matchId);
    sendEmail(d, m[c.by + 'Id'], `Reminder: your week ${c.week} check-in is ready. Please answer it on your Check-ins page.`);
    c.reminderSentAt = new Date(now).toISOString();
    sent++;
  });
  return sent;
}

/* What the admin still has to look at: answers the review flagged, and check-ins that were never answered. */
export function flagged(d, now = Date.now()) {
  return d.checkins.filter(c => activeMatch(d, c.matchId) &&
    ((c.review && c.review.status === 'open') || (!c.submittedAt && stateOf(c, now) === 'overdue' && !c.review)));
}

export function markReviewed(d, id, note) {
  const c = d.checkins.find(x => x.id === id);
  c.review = c.review || { verdict: 'needs attention', reason: 'The check-in was not answered in time.', source: 'preview' };
  Object.assign(c.review, { status: 'reviewed', adminNote: (note || '').trim() });
}
