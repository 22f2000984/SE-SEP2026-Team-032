/* Development only: puts the sample data into a known state so every screen can be photographed.
   Used by the router when the address has ?demo=... It is not part of the production build. */
import { respond, setStatus } from '../services/matches';
import { addFeedback, addConcern } from '../services/feedback';

export function applyDemoState(d, name) {
  const match = d.matches[0];
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
