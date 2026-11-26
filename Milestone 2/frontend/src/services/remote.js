/* The backend version of the data layer. The pages keep reading the one `db` object they always read; after every
   change we ask the backend for the current data and copy it into `db` (sync). All the field-name mapping between the
   backend (snake_case, profile ids) and the pages (camelCase, user ids) is in this file. */
import { db } from './db';
import { api, setToken, ApiError } from './api';
import { session, startSession } from './auth';
import { smartScore } from './smartMatch';

/* user id -> profile id, needed because the admin APIs use profile ids */
const profileId = { student: {}, mentor: {} };
let lastSync = 0;

const utc = text => (text ? text + 'Z' : null); // the backend sends UTC times without a Z
const defined = obj => Object.fromEntries(Object.entries(obj).filter(([, v]) => v !== undefined));

/* ---------- backend <-> page field names ---------- */
const toStudent = p => ({
  programme: p.programme_level || '', goals: p.career_goals || '', skills: p.skills || '', needsText: p.needs_text || '',
  topics: p.topics || [], format: p.mentoring_format, duration: p.expected_duration, preferences: p.preferences || '',
  availability: p.availability_note || '', looking: p.looking_for_mentor !== false, levels: p.levels || {}
});
const fromStudent = f => defined({
  programme_level: f.programme, career_goals: f.goals, skills: f.skills, needs_text: f.needsText, topics: f.topics,
  mentoring_format: f.format, expected_duration: f.duration, preferences: f.preferences, availability_note: f.availability
});
const toMentor = p => ({
  qualifications: p.qualifications || '', experience: p.experience_years || 0, topics: p.topics || [], bio: p.bio || '',
  skillsText: p.skills_text || '', status: p.profile_status, maxStudents: p.max_students
});
const fromMentor = f => defined({
  qualifications: f.qualifications, experience_years: f.experience === undefined ? undefined : Number(f.experience) || 0,
  bio: f.bio, skills_text: f.skillsText, max_students: f.maxStudents === undefined ? undefined : Number(f.maxStudents), topics: f.topics
});
const toSlots = p => (p.availability || []).map(s => ({ id: s.slot_id, mentorId: p.user_id, day: s.day_of_week, start: s.start_time, end: s.end_time }));
const person = (p, role) => ({ id: p.user_id, email: p.email || '', name: p.full_name, role });

function toMatch(m, studentUserId, mentorUserId) {
  return {
    id: m.match_id, studentId: studentUserId, mentorId: mentorUserId, status: m.status, notes: m.notes || '',
    proposedAt: utc(m.proposed_at), matchScore: m.match_score, scoreReasons: m.score_reasons,
    mentorResponse: m.mentor_response, studentResponse: m.student_response,
    mentorRespondedAt: utc(m.mentor_responded_at), studentRespondedAt: utc(m.student_responded_at), confirmedAt: utc(m.confirmed_at),
    log: (m.log || []).map(l => ({ from: l.from, to: l.to, at: utc(l.at), by: l.by }))
  };
}
const toFeedback = f => ({ id: f.feedback_id, matchId: f.match_id, authorId: f.author_id, rating: f.rating, comments: f.comments || '', at: utc(f.created_at) });
const toConcern = c => ({ id: c.concern_id, matchId: c.match_id, raisedBy: c.raised_by, text: c.text, status: c.status, at: utc(c.created_at) });
const toCheckIn = c => ({
  id: c.checkin_id, matchId: c.match_id, week: c.week, by: c.by, dueAt: utc(c.due_at), submittedAt: utc(c.submitted_at),
  rating: c.rating, comment: c.comment || '', reminderSentAt: null,
  review: c.review ? { verdict: c.review.verdict, reason: c.review.reason, status: c.review.status, source: c.review.source, adminNote: c.review.admin_note || '' } : null
});
const toEmail = e => ({ id: e.email_id, to: e.to_email, text: e.subject + ': ' + e.body, at: utc(e.created_at), status: e.status });
const notificationsOf = (list, userId) => list.slice().reverse().map(n => ({ id: n.notification_id, userId, text: n.message, at: utc(n.sent_at), read: n.is_read }));

/* ---------- sync: copy the backend's data into db ---------- */
async function loadAdmin(me) {
  const [students, mentors, matches, notes, feedback, concerns, emails] = await Promise.all([
    api('GET', '/api/admin/students'), api('GET', '/api/admin/mentors'), api('GET', '/api/admin/matches'), api('GET', '/api/notifications'),
    api('GET', '/api/admin/feedback'), api('GET', '/api/admin/concerns'), api('GET', '/api/admin/emails')
  ]);
  const toUser = {};
  const next = { users: [{ id: me.id, email: '', name: me.name, role: 'admin' }], students: {}, mentors: {}, slots: [] };
  profileId.student = {}; profileId.mentor = {};
  students.students.forEach(p => {
    next.users.push(person(p, 'student')); next.students[p.user_id] = toStudent(p);
    profileId.student[p.user_id] = p.student_id; toUser['s' + p.student_id] = p.user_id;
  });
  mentors.mentors.forEach(p => {
    next.users.push(person(p, 'mentor')); next.mentors[p.user_id] = toMentor(p); next.slots.push(...toSlots(p));
    profileId.mentor[p.user_id] = p.mentor_id; toUser['m' + p.mentor_id] = p.user_id;
  });
  next.matches = matches.matches.slice().reverse().map(m => toMatch(m, toUser['s' + m.student_id], toUser['m' + m.mentor_id]));
  next.notifications = notificationsOf(notes.notifications, me.id);
  next.feedback = feedback.feedback.slice().reverse().map(toFeedback);
  next.concerns = concerns.concerns.slice().reverse().map(toConcern);
  next.emails = emails.emails.map(toEmail);
  next.checkins = await loadCheckInsOfActiveMatches(matches.matches);
  return next;
}

/* The admin has no 'my check-ins' list: ask for the check-ins of each active match, week by week. */
async function loadCheckInsOfActiveMatches(matchList) {
  const active = matchList.filter(m => m.status === 'active');
  const answers = await Promise.all(active.map(m => api('GET', `/api/admin/matches/${m.match_id}/checkins`)));
  return answers.flatMap(a => a.checkins.map(toCheckIn));
}

async function loadStudent(me) {
  const [mine, matches, notes, feedback, concerns, checkins] = await Promise.all([api('GET', '/api/students/me'), api('GET', '/api/matches/me'), api('GET', '/api/notifications'), api('GET', '/api/feedback/me'), api('GET', '/api/concerns/me'), api('GET', '/api/checkins/me')]);
  const next = { users: [person(mine.profile, 'student')], students: { [me.id]: toStudent(mine.profile) }, mentors: {}, slots: [] };
  next.matches = matches.matches.slice().reverse().map(m => {
    next.users.push(person(m.other, 'mentor')); next.mentors[m.other.user_id] = toMentor(m.other); next.slots.push(...toSlots(m.other));
    return toMatch(m, me.id, m.other.user_id);
  });
  next.notifications = notificationsOf(notes.notifications, me.id);
  next.feedback = feedback.feedback.slice().reverse().map(toFeedback);
  next.concerns = concerns.concerns.slice().reverse().map(toConcern);
  next.checkins = checkins.checkins.map(toCheckIn);
  return next;
}

async function loadMentor(me) {
  const [mine, matches, notes, feedback, concerns, checkins] = await Promise.all([api('GET', '/api/mentors/me'), api('GET', '/api/matches/me'), api('GET', '/api/notifications'), api('GET', '/api/feedback/me'), api('GET', '/api/concerns/me'), api('GET', '/api/checkins/me')]);
  const next = { users: [person(mine.profile, 'mentor')], students: {}, mentors: { [me.id]: toMentor(mine.profile) }, slots: toSlots(mine.profile) };
  next.matches = matches.matches.slice().reverse().map(m => {
    next.users.push(person(m.other, 'student')); next.students[m.other.user_id] = toStudent(m.other);
    return toMatch(m, m.other.user_id, me.id);
  });
  next.notifications = notificationsOf(notes.notifications, me.id);
  next.feedback = feedback.feedback.slice().reverse().map(toFeedback);
  next.concerns = concerns.concerns.slice().reverse().map(toConcern);
  next.checkins = checkins.checkins.map(toCheckIn);
  return next;
}

const LOADERS = { admin: loadAdmin, student: loadStudent, mentor: loadMentor };

export async function syncDb(force = false) {
  const me = session.value;
  if (!me || (!force && Date.now() - lastSync < 1500)) return;
  const next = await LOADERS[me.role](me);
  if (me.role === 'admin') {
    next.matches.forEach(m => { // the Smart Match score is the offline stand-in until the AI agent exists (Sprint 2)
      const smart = smartScore(next, m.studentId, m.mentorId);
      m.smartScore = smart.total; m.smartReason = smart.reason;
    });
  }
  Object.assign(db, next); // the admin's check-ins and emails are loaded by loadAdmin
  lastSync = Date.now();
}

/* Runs one backend change, then re-reads the data. Returns an error message, or null when it worked. */
async function change(call) {
  try {
    await call();
    await syncDb(true);
    return null;
  } catch (e) {
    if (e instanceof ApiError) return e.message;
    throw e;
  }
}

/* ---------- the actions the pages use ---------- */
export async function login(email, password) {
  try {
    const data = await api('POST', '/api/auth/login', { email: email.trim(), password });
    setToken(data.token);
    startSession({ id: data.user.id, name: data.user.full_name, role: data.user.role });
    await syncDb(true);
    return { user: { role: data.user.role } };
  } catch (e) {
    if (e instanceof ApiError) return { error: e.message };
    throw e;
  }
}
export const register = form => change(() => api('POST', '/api/auth/register', { full_name: form.name.trim(), email: form.email.trim(), password: form.password, role: form.role }));

export const saveStudentProfile = (_id, f) => change(() => api('PUT', '/api/students/me', fromStudent(f)));
export const saveMentorProfile = (_id, f) => change(() => api('PUT', '/api/mentors/me', fromMentor(f)));
export const adminEditMentor = (id, f) => change(() => api('PUT', `/api/admin/mentors/${profileId.mentor[id]}`, fromMentor(f)));
export const verifyMentor = id => change(() => api('PATCH', `/api/admin/mentors/${profileId.mentor[id]}/status`, { status: 'verified' }));
export const addSlot = (_id, day, start, end) => change(() => api('POST', '/api/mentors/me/availability', { day_of_week: day, start_time: start, end_time: end }));
export const removeSlot = slotId => change(() => api('DELETE', `/api/mentors/me/availability/${slotId}`));

export const proposeMatch = (studentId, mentorId, notes) =>
  change(() => api('POST', '/api/admin/matches', { student_id: profileId.student[studentId], mentor_id: profileId.mentor[mentorId], notes }));
export const respond = (match, who, answer) => change(() => api('POST', `/api/matches/${match.id}/respond`, { answer }));
export const setStatus = (match, to) => change(() => api('PATCH', `/api/admin/matches/${match.id}/status`, { status: to }));

export const setLooking = (_id, looking) => change(() => (looking ? api('POST', '/api/students/me/mentor-request') : api('DELETE', '/api/students/me/mentor-request')));
export const sendFeedback = (matchId, _authorId, rating, comments) => change(() => api('POST', `/api/matches/${matchId}/feedback`, { rating: Number(rating), comments }));
export const sendConcern = (matchId, _userId, text) => change(() => api('POST', `/api/matches/${matchId}/concerns`, { text }));
export const submitCheckIn = (id, f) => change(() => api('POST', `/api/checkins/${id}/answer`, { rating: Number(f.rating), comment: f.comment }));
export const resolveConcern = id => change(() => api('PATCH', `/api/admin/concerns/${id}`, { status: 'resolved' }));

export const markReviewed = (id, note) => change(() => api('PATCH', `/api/admin/checkins/${id}/review`, { note: note || '' }));

/* Smart Match for one waiting student (user id). Returns { recs, source } or { error }.
   recs use the page's names: mentorId is the mentor's user id, total is the score out of 100. */
export async function smartRecommendations(studentUserId, limit) {
  try {
    const data = await api('GET', `/api/admin/students/${profileId.student[studentUserId]}/smart-recommendations?limit=${limit}`);
    const userOfMentor = Object.fromEntries(Object.entries(profileId.mentor).map(([user, profile]) => [profile, Number(user)]));
    const recs = data.recommendations.map(r => ({
      mentorId: userOfMentor[r.mentor_id], total: r.score, ruleTotal: r.rule_score, reason: r.reasons.join('; '), source: r.source
    }));
    return { recs, source: data.source };
  } catch (e) {
    if (e instanceof ApiError) return { error: e.message };
    throw e;
  }
}

/* Level quiz. loadQuiz returns { questions } or { error }; sendQuiz returns an error message or null. */
export async function loadQuiz() {
  try {
    return await api('GET', '/api/quiz');
  } catch (e) {
    if (e instanceof ApiError) return { error: e.message };
    throw e;
  }
}
export const sendQuiz = (topic, answers) => change(() => api('POST', '/api/students/me/quiz', { topic, answers }));
