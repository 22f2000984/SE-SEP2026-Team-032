/* The backend mode: the data from the API is copied into db with the page's field names and user ids. */
import { describe, it, expect, beforeEach, vi } from 'vitest';

const ANSWERS = {
  'POST /api/auth/login': { token: 'T', user: { id: 9, email: 'admin@client.test', full_name: 'Admin', role: 'admin' } },
  'GET /api/admin/students': { students: [{ student_id: 1, user_id: 11, full_name: 'Asha Verma', email: 'asha@ds.study.iitm.ac.in', programme_level: 'Diploma', career_goals: 'Data analytics', skills: 'SQL', needs_text: 'I need a portfolio', mentoring_format: 'Video call', expected_duration: '3 months', preferences: '', availability_note: 'Weekends', topics: ['Data Science'] }] },
  'GET /api/admin/mentors': { mentors: [{ mentor_id: 4, user_id: 12, full_name: 'Dr. Meera Iyer', email: 'meera@mentor.test', qualifications: 'PhD', experience_years: 12, bio: '', skills_text: 'SQL and Python portfolio projects', profile_status: 'verified', max_students: 3, topics: ['Data Science'], availability: [{ slot_id: 7, day_of_week: 'Saturday', start_time: '18:00', end_time: '20:00' }] }] },
  'GET /api/admin/matches': { matches: [{ match_id: 5, student_id: 1, mentor_id: 4, status: 'proposed', mentor_response: 'pending', student_response: 'accepted', match_score: 100, score_reasons: 'x', notes: '', proposed_at: '2026-11-20T10:00:00', student_responded_at: '2026-11-20T11:00:00', mentor_responded_at: null, confirmed_at: null, log: [{ from: '-', to: 'proposed', at: '2026-11-20T10:00:00', by: 'Admin' }] }] },
  'GET /api/admin/feedback': { feedback: [{ feedback_id: 3, match_id: 5, author_id: 11, rating: 4, comments: 'Helpful', created_at: '2026-11-21T09:00:00' }] },
  'GET /api/admin/concerns': { concerns: [{ concern_id: 6, match_id: 5, raised_by: 11, text: 'Mentor is late', status: 'open', created_at: '2026-11-21T10:00:00', resolved_at: null }] },
  'GET /api/admin/emails': { emails: [{ email_id: 1, to_email: 'asha@ds.study.iitm.ac.in', subject: 'Check-in reminder', body: 'Your week 1 check-in is ready.', status: 'not_configured', created_at: '2026-11-21T09:30:00' }] },
  'GET /api/notifications': { notifications: [{ notification_id: 2, message: 'newer', is_read: false, sent_at: '2026-11-20T12:00:00' }, { notification_id: 1, message: 'older', is_read: false, sent_at: '2026-11-20T10:00:00' }] }
};

let calls;
beforeEach(() => {
  vi.resetModules();
  vi.stubEnv('VITE_API_URL', 'http://api.test/');
  calls = [];
  vi.stubGlobal('fetch', async (url, options) => {
    const key = `${options.method} ${url.replace('http://api.test', '')}`;
    calls.push({ key, options });
    const body = ANSWERS[key];
    if (!body) return { ok: false, status: 404, json: async () => ({ error: 'Not found.' }) };
    return { ok: true, status: 200, json: async () => body };
  });
});

async function loadModules() {
  const remote = await import('../src/services/remote');
  const { db } = await import('../src/services/db');
  const { session } = await import('../src/services/auth');
  return { remote, db, session };
}

describe('backend mode', () => {
  it('logs in and copies the admin data into db with user ids and page field names', async () => {
    const { remote, db, session } = await loadModules();
    const result = await remote.login('admin@client.test', 'demo123');
    expect(result.user.role).toBe('admin');
    expect(session.value).toEqual({ id: 9, name: 'Admin', role: 'admin' });
    expect(db.students[11]).toMatchObject({ programme: 'Diploma', goals: 'Data analytics', needsText: 'I need a portfolio', format: 'Video call' });
    expect(db.mentors[12]).toMatchObject({ experience: 12, maxStudents: 3, status: 'verified', skillsText: 'SQL and Python portfolio projects' });
    expect(db.slots).toEqual([{ id: 7, mentorId: 12, day: 'Saturday', start: '18:00', end: '20:00' }]);
    expect(db.users.map(u => u.role).sort()).toEqual(['admin', 'mentor', 'student']);
  });

  it('maps matches to user ids and adds the offline Smart Match score', async () => {
    const { remote, db } = await loadModules();
    await remote.login('admin@client.test', 'demo123');
    const m = db.matches[0];
    expect(m).toMatchObject({ id: 5, studentId: 11, mentorId: 12, status: 'proposed', studentResponse: 'accepted' });
    expect(m.proposedAt).toBe('2026-11-20T10:00:00Z');
    expect(m.log).toHaveLength(1);
    expect(typeof m.smartScore).toBe('number');
  });

  it('copies feedback and concerns from the backend into db', async () => {
    const { remote, db } = await loadModules();
    await remote.login('admin@client.test', 'demo123');
    expect(db.feedback).toHaveLength(1);
    expect(db.feedback[0]).toMatchObject({ id: 3, matchId: 5, authorId: 11, rating: 4, comments: 'Helpful' });
    expect(db.concerns).toHaveLength(1);
    expect(db.concerns[0]).toMatchObject({ id: 6, matchId: 5, text: 'Mentor is late', status: 'open' });
  });

  it('shows notifications oldest first, as the pages expect', async () => {
    const { remote, db } = await loadModules();
    await remote.login('admin@client.test', 'demo123');
    expect(db.notifications.map(n => n.text)).toEqual(['older', 'newer']);
    expect(db.notifications[0].userId).toBe(9);
  });

  it('sends the token and backend profile ids when proposing a match', async () => {
    const { remote } = await loadModules();
    await remote.login('admin@client.test', 'demo123');
    ANSWERS['POST /api/admin/matches'] = { match: {} };
    await remote.proposeMatch(11, 12, 'because');
    const call = calls.find(c => c.key === 'POST /api/admin/matches');
    expect(JSON.parse(call.options.body)).toEqual({ student_id: 1, mentor_id: 4, notes: 'because' });
    delete ANSWERS['POST /api/admin/matches'];
  });

  it('returns the backend error message instead of throwing', async () => {
    const { remote } = await loadModules();
    await remote.login('admin@client.test', 'demo123');
    const problem = await remote.verifyMentor(12); // no answer prepared, so the fake server says 404
    expect(problem).toBe('Not found.');
  });
  it('a student sees the check-ins from the backend and answers one', async () => {
    const original = { ...ANSWERS };
    Object.assign(ANSWERS, {
      'POST /api/auth/login': { token: 'S', user: { id: 11, email: 'asha@ds.study.iitm.ac.in', full_name: 'Asha Verma', role: 'student' } },
      'GET /api/students/me': { profile: { student_id: 1, user_id: 11, full_name: 'Asha Verma', email: 'asha@ds.study.iitm.ac.in', programme_level: 'Diploma', career_goals: 'Data', topics: ['Data Science'] } },
      'GET /api/matches/me': { matches: [] },
      'GET /api/feedback/me': { feedback: [] },
      'GET /api/concerns/me': { concerns: [] },
      'GET /api/checkins/me': { checkins: [{ checkin_id: 8, match_id: 5, week: 1, by: 'student', due_at: '2026-11-21T10:00:00', submitted_at: null, rating: null, comment: '', review: null }] },
      'POST /api/checkins/8/answer': { checkin: { checkin_id: 8 } }
    });
    try {
      const { remote, db } = await loadModules();
      await remote.login('asha@ds.study.iitm.ac.in', 'demo123');
      expect(db.checkins).toHaveLength(1);
      expect(db.checkins[0]).toMatchObject({ id: 8, matchId: 5, week: 1, by: 'student', submittedAt: null, dueAt: '2026-11-21T10:00:00Z' });
      const error = await remote.submitCheckIn(8, { rating: '4', comment: 'Good' });
      expect(error).toBeNull();
      const sent = calls.find(c => c.key === 'POST /api/checkins/8/answer');
      expect(JSON.parse(sent.options.body)).toEqual({ rating: 4, comment: 'Good' });
    } finally {
      Object.keys(ANSWERS).forEach(k => delete ANSWERS[k]);
      Object.assign(ANSWERS, original);
    }
  });

  it('the admin gets the email log, and the check-ins of active matches', async () => {
    const original = { ...ANSWERS };
    ANSWERS['GET /api/admin/matches'] = { matches: [{ ...ANSWERS['GET /api/admin/matches'].matches[0], status: 'active' }] };
    ANSWERS['GET /api/admin/matches/5/checkins'] = { checkins: [{ checkin_id: 8, match_id: 5, week: 1, by: 'student', due_at: '2026-11-21T10:00:00', submitted_at: '2026-11-21T11:00:00', rating: 2, comment: 'late', review: { verdict: 'needs attention', reason: 'low', status: 'open', source: 'rules', admin_note: '' } }] };
    ANSWERS['PATCH /api/admin/checkins/8/review'] = { checkin: { checkin_id: 8 } };
    try {
      const { remote, db } = await loadModules();
      await remote.login('admin@client.test', 'demo123');
      expect(db.emails).toHaveLength(1);
      expect(db.emails[0]).toMatchObject({ to: 'asha@ds.study.iitm.ac.in', status: 'not_configured' });
      expect(db.checkins[0]).toMatchObject({ id: 8, rating: 2, review: { verdict: 'needs attention', status: 'open' } });
      expect(await remote.markReviewed(8, 'called')).toBeNull();
      expect(JSON.parse(calls.find(c => c.key === 'PATCH /api/admin/checkins/8/review').options.body)).toEqual({ note: 'called' });
    } finally {
      Object.keys(ANSWERS).forEach(k => delete ANSWERS[k]);
      Object.assign(ANSWERS, original);
    }
  });

  it('Smart Match recommendations are mapped to the names the page uses', async () => {
    const original = { ...ANSWERS };
    ANSWERS['GET /api/admin/students/1/smart-recommendations?limit=3'] = { student_id: 1, source: 'rules', recommendations: [{ mentor_id: 4, mentor_name: 'Dr. Meera Iyer', score: 80, text_fit: 70, rule_score: 100, source: 'rules', reasons: ['Both describe: sql', 'Shared topics: Data Science'] }] };
    try {
      const { remote } = await loadModules();
      await remote.login('admin@client.test', 'demo123');
      const answer = await remote.smartRecommendations(11, 3);
      expect(answer.source).toBe('rules');
      expect(answer.recs[0]).toMatchObject({ mentorId: 12, total: 80, ruleTotal: 100, source: 'rules' });
      expect(answer.recs[0].reason).toContain('Both describe: sql');
    } finally {
      Object.keys(ANSWERS).forEach(k => delete ANSWERS[k]);
      Object.assign(ANSWERS, original);
    }
  });

  it('sends the quiz answers for a topic', async () => {
    ANSWERS['POST /api/students/me/quiz'] = { result: { topic: 'Data Science', level: 'beginner' } };
    try {
      const { remote } = await loadModules();
      await remote.login('admin@client.test', 'demo123');
      expect(await remote.sendQuiz('Data Science', [0, 0, 0, 0, 0])).toBeNull();
      expect(JSON.parse(calls.find(c => c.key === 'POST /api/students/me/quiz').options.body)).toEqual({ topic: 'Data Science', answers: [0, 0, 0, 0, 0] });
    } finally {
      delete ANSWERS['POST /api/students/me/quiz'];
    }
  });
});
