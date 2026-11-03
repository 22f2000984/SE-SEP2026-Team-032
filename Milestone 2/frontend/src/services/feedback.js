/* Student feedback and concerns about a match. */
import { userName } from '../utils/format';
import { nextId } from './ids';
import { notifyAdmins } from './notifications';

export function addFeedback(d, matchId, authorId, rating, comments) {
  d.feedback.push({ id: nextId(d), matchId, authorId, rating: Number(rating), comments: (comments || '').trim(), at: new Date().toISOString() });
}
export function addConcern(d, matchId, userId, text) {
  const t = (text || '').trim();
  if (!t) return 'Describe your concern first.';
  d.concerns.push({ id: nextId(d), matchId, raisedBy: userId, text: t, status: 'open', at: new Date().toISOString() });
  notifyAdmins(d, `${userName(d, userId)} raised a concern about a match.`);
  return null;
}
export function resolveConcern(d, concernId) {
  d.concerns.find(c => c.id === concernId).status = 'resolved';
}
