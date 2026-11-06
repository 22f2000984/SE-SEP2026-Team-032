/* Smart Match (design preview). In the finished platform an AI agent reads what the student and the mentor wrote
   and returns a score with a reason. This file is the offline stand-in with the same inputs and outputs, so the pages
   can be shown and tested without a backend. Pure functions: they read the data and return results. */
import { SMART } from '../config/constants';
import { eligible, scoreMatch } from './matching';

const STOP = new Set(('i a an and are as at be been but by can do for from get has have help how in into is it its me my need needs of on or our so that the their them then there these this to want wants was we what when which who will with would you your am about also very much more most like any all some such than too').split(' '));

function stem(word) {
  return word.length > 5 ? word.replace(/(ing|ed|es|s)$/, '') : word.replace(/s$/, '');
}

/* The meaningful words of a text, as a map from word stem to the word as written. */
export function keywords(text) {
  const out = new Map();
  (String(text || '').toLowerCase().match(/[a-z]+/g) || []).forEach(w => {
    if (w.length < 3 || STOP.has(w)) return;
    const k = stem(w);
    if (!out.has(k)) out.set(k, w);
  });
  return out;
}

/* Score out of 100 with a reason. 60 points come from the wording of the two texts, 40 from the rule score. */
export function smartScore(d, studentId, mentorId) {
  const s = d.students[studentId], m = d.mentors[mentorId];
  const rule = scoreMatch(d, studentId, mentorId);
  const need = keywords(`${s.needsText || ''} ${s.goals || ''}`);
  const offer = keywords(`${m.skillsText || ''} ${m.bio || ''} ${m.qualifications || ''}`);
  const shared = [...need.keys()].filter(k => offer.has(k)).map(k => need.get(k));
  const base = Math.min(need.size, SMART.maxKeywords);
  const text = base ? Math.min(1, shared.length / base) : 0;
  const total = Math.round(SMART.textWeight * text + (SMART.ruleWeight / 100) * rule.total);
  const topics = (s.topics || []).filter(t => (m.topics || []).includes(t));
  const reason = [
    shared.length ? `Both describe: ${shared.slice(0, 6).join(', ')}` : 'The free-text answers share no wording',
    `covers ${topics.length} of ${(s.topics || []).length} wanted topics`,
    `${m.experience || 0} years of experience`
  ].join('; ');
  return { total, ruleTotal: rule.total, reason, shared };
}

/* Best eligible mentors for one student by Smart Match score. */
export function recommendSmart(d, studentId, n) {
  return Object.keys(d.mentors).map(Number)
    .filter(mentorId => !eligible(d, studentId, mentorId))
    .map(mentorId => ({ mentorId, ...smartScore(d, studentId, mentorId) }))
    .sort((a, b) => b.total - a.total)
    .slice(0, n);
}
