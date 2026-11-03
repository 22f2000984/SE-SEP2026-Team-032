/* Everything that creates or changes a match: propose, answer, confirm, cancel, complete. */
import { NEXT_STEP } from '../config/constants';
import { userName } from '../utils/format';
import { eligible, scoreMatch } from './matching';
import { nextId } from './ids';
import { notify, notifyAdmins } from './notifications';

export function bothAccepted(m) {
  return m.mentorResponse === 'accepted' && m.studentResponse === 'accepted';
}

/* The only way a match is created. Returns an error message, or null on success. */
export function proposeMatch(d, studentId, mentorId, notes, by) {
  const why = eligible(d, studentId, mentorId);
  if (why) return why;
  const sc = scoreMatch(d, studentId, mentorId), now = new Date().toISOString();
  d.matches.push({
    id: nextId(d), studentId, mentorId, status: 'proposed', notes: notes || '', proposedAt: now,
    matchScore: sc.total, scoreReasons: sc.reasons.join('; '),
    mentorResponse: 'pending', studentResponse: 'pending', mentorRespondedAt: null, studentRespondedAt: null, confirmedAt: null,
    log: [{ from: '-', to: 'proposed', at: now, by }]
  });
  notify(d, mentorId, 'A new student match is waiting for your response.');
  notify(d, studentId, 'A mentor has been proposed for you. Please accept or decline.');
  return null;
}

/* who is 'mentor' or 'student'; answer is 'accepted' or 'declined'. The admin is told, and when both accept, can confirm. */
export function respond(d, m, who, answer) {
  m[who + 'Response'] = answer;
  m[who + 'RespondedAt'] = new Date().toISOString();
  const sName = userName(d, m.studentId), mName = userName(d, m.mentorId), name = who === 'mentor' ? mName : sName;
  notifyAdmins(d, `${name} (${who}) ${answer} the proposed match ${sName} / ${mName}.`);
  if (bothAccepted(m)) notifyAdmins(d, `Both accepted: ${sName} / ${mName} is ready for you to confirm.`);
}

/* Change the status of a match. Confirming a proposal needs both answers to be "accepted".
   Returns false when the change is refused. */
export function setStatus(d, m, to, by) {
  if (m.status === 'proposed' && to === 'active' && !bothAccepted(m)) return false;
  if (to === 'active') m.confirmedAt = new Date().toISOString();
  m.log.push({ from: m.status, to, at: new Date().toISOString(), by });
  m.status = to;
  const sName = userName(d, m.studentId), mName = userName(d, m.mentorId);
  notify(d, m.studentId, `Your mentoring match with ${mName} is now ${to}. Next step: ${NEXT_STEP[to]}`);
  notify(d, m.mentorId, `Your match with ${sName} is now ${to}.${to === 'active' ? ' Next step: contact the student to agree the first session.' : ''}`);
  notifyAdmins(d, `Match ${sName} / ${mName} is now ${to}.`);
  return true;
}
