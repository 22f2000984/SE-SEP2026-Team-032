/* Mentorship Pulse review (design preview). In the finished platform an AI agent reads each check-in and decides
   whether the admin must look at it. This is the offline stand-in with the same input and output. It only flags;
   it never changes a match. Pure function. */
import { LOW_RATING, VERDICTS } from '../config/constants';

const WORRYING = ['not responding', 'no response', 'cancelled', 'canceled', 'no show', 'unhelpful', 'rude', 'confused', 'ignored', 'hard to reach', 'clash', 'stopped'];

export function reviewCheckIn({ rating, comment }) {
  const text = String(comment || '').toLowerCase();
  const hits = WORRYING.filter(w => text.includes(w));
  const reasons = [];
  let level = 0;
  if (rating <= LOW_RATING) { level = 2; reasons.push(`The rating of ${rating}/5 is low`); }
  else if (rating === 3) { level = 1; reasons.push('The rating of 3/5 is middling'); }
  if (hits.length) { level = Math.max(level, 1); reasons.push(`The comment mentions: ${hits.join(', ')}`); }
  return {
    verdict: VERDICTS[level],
    reason: reasons.length ? reasons.join('. ') + '.' : 'The rating is good and the comment shows no worry.',
    status: level ? 'open' : 'ok',
    source: 'preview',
    adminNote: ''
  };
}
