/* Development only: puts the sample data into a known state so every screen can be photographed.
   Used by the router when the address has ?demo=... It is not part of the production build. */
import { respond, setStatus, proposeMatch } from '../services/matches';
import { addFeedback, addConcern } from '../services/feedback';
import { checkInsOf, submitCheckIn, sendReminders } from '../services/checkins';

export function applyDemoState(d, name) {
  const match = d.matches[0];
  if (name === 'pulse') return pulseState(d, match);
  if (name === 'busy') return busyState(d, match);
  if (name === 'mentor-accepted') {
    respond(d, match, 'mentor', 'accepted');
  } else if (name === 'ready' || name === 'active') {
    respond(d, match, 'mentor', 'accepted');
    respond(d, match, 'student', 'accepted');
    if (name === 'active') {
      setStatus(d, match, 'active', 'Admin');
      addFeedback(d, match.id, 1, 5, 'Very helpful first session.');
      addConcern(d, match.id, 1, 'Sessions on Saturday clash with my exam.');
    }
  }
}

/* An active match 15 days old: the mentor's week 1 answer was flagged by the review, the student's week 1 check-in
   was never answered, and week 2 is due for both. */
function pulseState(d, match) {
  respond(d, match, 'mentor', 'accepted');
  respond(d, match, 'student', 'accepted');
  setStatus(d, match, 'active', 'Admin');
  match.confirmedAt = new Date(Date.now() - 15 * 864e5).toISOString();
  checkInsOf(d, match.id).forEach(c => { c.dueAt = new Date(new Date(match.confirmedAt).getTime() + c.week * 7 * 864e5).toISOString(); });
  const mentorWeek1 = checkInsOf(d, match.id, 'mentor').find(c => c.week === 1);
  submitCheckIn(d, mentorWeek1.id, { rating: 2, comment: 'Asha has not replied to my messages, so we could not meet.' });
  sendReminders(d);
}

/* A platform in use: two active matches with answered check-ins, some feedback and a concern, so the admin overview has numbers to show. */
function busyState(d, match) {
  pulseState(d, match);
  addFeedback(d, match.id, 1, 5, 'Very helpful first session.');
  proposeMatch(d, 6, 7, '', 'Admin');
  const second = d.matches[d.matches.length - 1];
  respond(d, second, 'mentor', 'accepted');
  respond(d, second, 'student', 'accepted');
  setStatus(d, second, 'active', 'Admin');
  second.confirmedAt = new Date(Date.now() - 22 * 864e5).toISOString();
  checkInsOf(d, second.id).forEach(c => { c.dueAt = new Date(new Date(second.confirmedAt).getTime() + c.week * 7 * 864e5).toISOString(); });
  const answers = [['student', 1, 5, 'Priya gave me a clear plan.'], ['mentor', 1, 4, 'Neha is keen and prepared.'], ['student', 2, 4, 'Good session on requirements.'], ['mentor', 2, 3, 'We missed a week, back on track now.']];
  answers.forEach(([by, week, rating, comment]) => submitCheckIn(d, checkInsOf(d, second.id, by).find(c => c.week === week).id, { rating, comment }));
  addFeedback(d, second.id, 6, 4, 'Helpful, would like more mock interviews.');
  addConcern(d, second.id, 6, 'Sessions on Saturday clash with my exam.');
  sendReminders(d);
}
