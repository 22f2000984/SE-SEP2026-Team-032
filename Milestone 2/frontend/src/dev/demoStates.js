/* Development only: puts the sample data into a known state so every screen can be photographed.
   Used by the router when the address has ?demo=... It is not part of the production build. */
import { respond, setStatus } from '../services/matches';
import { addFeedback, addConcern } from '../services/feedback';
import { checkInsOf, submitCheckIn, sendReminders } from '../services/checkins';

export function applyDemoState(d, name) {
  const match = d.matches[0];
  if (name === 'pulse') return pulseState(d, match);
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
