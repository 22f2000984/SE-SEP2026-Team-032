/* Shared helpers for the Milestone 2 prototype.
   All data is sample data kept in the browser (localStorage). There is no backend. */
const DB_KEY = 't32_data_v3', USER_KEY = 't32_user';
const STATUSES = ['proposed', 'active', 'completed', 'cancelled'];
const NEXT = { proposed: ['active', 'cancelled'], active: ['completed', 'cancelled'], completed: [], cancelled: [] };
const NAVS = {
  student: [['student.html', 'Dashboard'], ['student-profile.html', 'My Profile'], ['student-mentor.html', 'My Mentor']],
  mentor: [['mentor.html', 'Dashboard'], ['mentor-profile.html', 'My Profile']],
  admin: [['admin.html', 'Overview'], ['admin-students.html', 'Students'], ['admin-mentors.html', 'Mentors'], ['admin-matches.html', 'Matches']]
};
const FORMATS = ['No preference', 'Video call', 'Phone call', 'Messaging'], DURATIONS = ['Not sure yet', '1 month', '3 months', '6 months'];
const NEXT_STEP = { proposed: 'Accept or decline the proposed match. The admin confirms it once both the mentor and the student have accepted.', active: 'Agree the first session with your mentor. Share feedback or a concern at any time.', completed: 'Mentoring has finished. Please leave feedback if you have not yet.', cancelled: 'This match has ended. The admin will arrange a new one.' };
const TOPICS = ['Data Science', 'Web Development', 'Career Switching', 'Interview Preparation', 'Product Management', 'Higher Studies', 'Entrepreneurship', 'Cloud and DevOps'];
const WEIGHTS = { topics: 70, experience: 30 };
const MIN_SCORE = 40, DEFAULT_CAPACITY = 3;
const daysAgo = n => new Date(Date.now() - n * 864e5).toISOString();

function seed() {
  const d = {
    nextId: 100,
    users: [
      { id: 1, email: 'asha@student.test', password: 'demo123', name: 'Asha Verma', role: 'student' },
      { id: 2, email: 'rohan@student.test', password: 'demo123', name: 'Rohan Das', role: 'student' },
      { id: 3, email: 'meera@mentor.test', password: 'demo123', name: 'Dr. Meera Iyer', role: 'mentor' },
      { id: 4, email: 'karan@mentor.test', password: 'demo123', name: 'Karan Shah', role: 'mentor' },
      { id: 5, email: 'admin@client.test', password: 'demo123', name: 'Admin', role: 'admin' },
      { id: 6, email: 'neha@student.test', password: 'demo123', name: 'Neha Joshi', role: 'student' },
      { id: 7, email: 'priya@mentor.test', password: 'demo123', name: 'Priya Nair', role: 'mentor' }
    ],
    students: {
      1: { programme: 'Diploma', goals: 'Move into data analytics', skills: 'Python, SQL', topics: ['Data Science', 'Career Switching'], format: 'Video call', duration: '3 months', preferences: 'Weekend calls', availability: 'Weekend evenings' },
      2: { programme: 'Foundation', goals: 'Prepare for software interviews', skills: 'HTML, JavaScript', topics: ['Interview Preparation', 'Web Development'], format: 'Messaging', duration: '1 month', preferences: '', availability: 'Sunday afternoons' },
      6: { programme: 'Degree', goals: 'Plan a product management career', skills: 'Excel, communication', topics: ['Product Management', 'Career Switching'], format: 'Phone call', duration: '6 months', preferences: 'Short weekly calls', availability: 'Sunday and Wednesday evenings' }
    },
    mentors: {
      3: { qualifications: 'PhD, Data Science', experience: 12, topics: ['Data Science', 'Career Switching'], bio: 'Leads an analytics team and mentors early-career students.', status: 'verified', maxStudents: 3 },
      4: { qualifications: 'B.Tech', experience: 5, topics: ['Web Development'], bio: '', status: 'pending', maxStudents: 2 },
      7: { qualifications: 'MBA, Product Manager', experience: 8, topics: ['Product Management', 'Interview Preparation', 'Career Switching'], bio: 'Product manager who coaches students on product careers and interviews.', status: 'verified', maxStudents: 2 }
    },
    slots: [
      { id: 1, mentorId: 3, day: 'Saturday', start: '18:00', end: '20:00' },
      { id: 2, mentorId: 7, day: 'Sunday', start: '17:00', end: '19:00' },
      { id: 3, mentorId: 7, day: 'Wednesday', start: '18:00', end: '19:30' }
    ],
    matches: [{ id: 1, studentId: 1, mentorId: 3, status: 'proposed', notes: 'Goal fit: analytics', proposedAt: daysAgo(5), mentorResponse: 'pending', studentResponse: 'pending', mentorRespondedAt: null, studentRespondedAt: null, confirmedAt: null, log: [{ from: '-', to: 'proposed', at: daysAgo(5), by: 'Admin' }] }],
    concerns: [], feedback: [],
    notifications: [{ id: 1, userId: 3, text: 'A new student match is waiting for your response.', at: daysAgo(5), read: false }, { id: 2, userId: 1, text: 'A mentor has been proposed for you. Please accept or decline.', at: daysAgo(5), read: false }]
  };
  const sc = scoreMatch(d, 1, 3); d.matches[0].matchScore = sc.total; d.matches[0].scoreReasons = sc.reasons.join('; ');
  return d;
}
function load() {
  try { const d = JSON.parse(localStorage.getItem(DB_KEY)); if (d && d.users) return d; } catch (e) { /* fall through */ }
  const d = seed(); save(d); return d;
}
function save(d) { try { localStorage.setItem(DB_KEY, JSON.stringify(d)); } catch (e) { /* storage blocked */ } }
function resetDemo() { try { localStorage.removeItem(DB_KEY); sessionStorage.removeItem(USER_KEY); } catch (e) {} location.href = 'index.html'; }
function id(d) { return d.nextId++; }
function me() { try { return JSON.parse(sessionStorage.getItem(USER_KEY)); } catch (e) { return null; } }
function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }
function pill(s) { return `<span class="pill ${esc(s).replace(/[^a-z]/g, '')}">${esc(s)}</span>`; }
function when(iso) { return new Date(iso).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }); }
function userName(d, uid) { const u = d.users.find(x => x.id === uid); return u ? u.name : 'Unknown'; }
function notify(d, userId, text) { d.notifications.push({ id: id(d), userId, text, at: new Date().toISOString(), read: false }); }

function guard(role) {
  const u = me();
  if (!u) { location.href = 'index.html'; return null; }
  if (role && u.role !== role) { location.href = 'index.html'; return null; }
  const links = NAVS[u.role].map(([h, t]) => `<a href="${h}" class="${location.pathname.endsWith(h) ? 'active' : ''}">${t}</a>`).join('');
  document.body.insertAdjacentHTML('afterbegin',
    `<header><a class="brand" href="${NAVS[u.role][0][0]}">IITM · MENTOR CONNECT</a><nav class="nav">${links}<span class="who">${esc(u.name)}${u.role === 'admin' ? '' : ` (${u.role})`}</span><a href="#" id="logout">Log out</a></nav></header>`);
  document.getElementById('logout').onclick = e => { e.preventDefault(); sessionStorage.removeItem(USER_KEY); location.href = 'index.html'; };
  document.body.insertAdjacentHTML('beforeend', '<div class="toast" id="toast"></div><footer>Team 032 – Himalayan Coders · Milestone 2 frontend prototype (sample data, no backend)</footer>');
  return u;
}
function toast(msg) {
  const t = document.getElementById('toast'); if (!t) return;
  t.textContent = msg; t.classList.add('show'); setTimeout(() => t.classList.remove('show'), 2200);
}
function bothAccepted(m) { return m.mentorResponse === 'accepted' && m.studentResponse === 'accepted'; }
function setStatus(d, m, to, by) {
  if (m.status === 'proposed' && to === 'active' && !bothAccepted(m)) return false;
  if (to === 'active') m.confirmedAt = new Date().toISOString();
  m.log.push({ from: m.status, to, at: new Date().toISOString(), by });
  m.status = to;
  const sName = userName(d, m.studentId), mName = userName(d, m.mentorId);
  notify(d, m.studentId, `Your mentoring match with ${mName} is now ${to}. Next step: ${NEXT_STEP[to]}`);
  notify(d, m.mentorId, `Your match with ${sName} is now ${to}.${to === 'active' ? ' Next step: contact the student to agree the first session.' : ''}`);
  d.users.filter(u => u.role === 'admin').forEach(a => notify(d, a.id, `Match ${sName} / ${mName} is now ${to}.`));
  return true;
}
/* who is 'mentor' or 'student'; answer is 'accepted' or 'declined'. The admin is told, and when both accept, can confirm. */
function respond(d, m, who, answer) {
  m[who + 'Response'] = answer; m[who + 'RespondedAt'] = new Date().toISOString();
  const sName = userName(d, m.studentId), mName = userName(d, m.mentorId), name = who === 'mentor' ? mName : sName;
  const admins = d.users.filter(u => u.role === 'admin');
  admins.forEach(a => notify(d, a.id, `${name} (${who}) ${answer} the proposed match ${sName} / ${mName}.`));
  if (bothAccepted(m)) admins.forEach(a => notify(d, a.id, `Both accepted: ${sName} / ${mName} is ready for you to confirm.`));
}

/* Demo shortcut used for screenshots: page.html?as=student|mentor|admin signs in as the sample user. */
(function () {
  const as = new URLSearchParams(location.search).get('as'), ids = { student: 1, mentor: 3, admin: 5 };
  if (!as || !ids[as] || me()) return;
  const u = load().users.find(x => x.id === ids[as]);
  try { sessionStorage.setItem(USER_KEY, JSON.stringify({ id: u.id, name: u.name, role: u.role })); } catch (e) {}
})();


/* ---------- Mentor availability and capacity ---------- */
function slotText(d, mid) { const t = d.slots.filter(x => x.mentorId === mid).map(x => `${x.day} ${x.start}-${x.end}`).join(', '); return t || 'no slots added'; }
function used(d, mid) { return d.matches.filter(m => m.mentorId === mid && ['proposed', 'active'].includes(m.status)).length; }
function maxOf(d, mid) { return d.mentors[mid].maxStudents || DEFAULT_CAPACITY; }
function hasOpenMatch(d, sid) { return d.matches.some(m => m.studentId === sid && ['proposed', 'active'].includes(m.status)); }
function capBar(d, mid) { const u = used(d, mid), mx = maxOf(d, mid); return `<span class="scorebar cap ${u >= mx ? 'full' : ''}"><span style="width:${Math.min(100, u / mx * 100)}%"></span></span> ${u} of ${mx} places used`; }
function topicsText(a) { return (a && a.length) ? a.join(', ') : '-'; }

/* ---------- Matching: eligibility, score, recommendations ---------- */
/* Returns null when the pair may be proposed, otherwise the reason it may not. */
function eligible(d, sid, mid) {
  if (!d.mentors[mid] || d.mentors[mid].status !== 'verified') return 'The mentor is not verified yet.';
  if (used(d, mid) >= maxOf(d, mid)) return 'This mentor has no free places.';
  if (hasOpenMatch(d, sid)) return 'This student already has an open match.';
  return null;
}
/* Score out of 100: topics 70 (share of the student's wanted topics the mentor covers) and experience 30 (years, up to 10).
   Free places do not add points; they decide whether a pair is allowed at all. */
function scoreMatch(d, sid, mid) {
  const s = d.students[sid], m = d.mentors[mid], reasons = [];
  const shared = (s.topics || []).filter(t => (m.topics || []).includes(t));
  const topics = s.topics && s.topics.length ? Math.round(WEIGHTS.topics * shared.length / s.topics.length) : 0;
  reasons.push(shared.length ? `Shared topics: ${shared.join(', ')}` : 'No shared topics');
  const experience = Math.round(WEIGHTS.experience * Math.min(m.experience || 0, 10) / 10);
  reasons.push(`${m.experience || 0} years of experience`);
  const free = Math.max(0, maxOf(d, mid) - used(d, mid));
  reasons.push(`${free} of ${maxOf(d, mid)} places free`);
  return { total: topics + experience, parts: { topics, experience }, reasons };
}
/* Best eligible mentors for one student, highest score first. */
function recommend(d, sid, n) {
  return Object.keys(d.mentors).map(Number).filter(mid => !eligible(d, sid, mid)).map(mid => ({ mentorId: mid, ...scoreMatch(d, sid, mid) })).sort((a, b) => b.total - a.total).slice(0, n);
}
function waitingStudents(d) { return d.users.filter(u => u.role === 'student' && !hasOpenMatch(d, u.id)); }
/* The only way a match is created. Returns an error message, or null on success. */
function proposeMatch(d, sid, mid, notes, by) {
  const why = eligible(d, sid, mid); if (why) return why;
  const sc = scoreMatch(d, sid, mid), now = new Date().toISOString();
  d.matches.push({ id: id(d), studentId: sid, mentorId: mid, status: 'proposed', notes: notes || '', proposedAt: now, matchScore: sc.total, scoreReasons: sc.reasons.join('; '), mentorResponse: 'pending', studentResponse: 'pending', mentorRespondedAt: null, studentRespondedAt: null, confirmedAt: null, log: [{ from: '-', to: 'proposed', at: now, by }] });
  notify(d, mid, 'A new student match is waiting for your response.');
  notify(d, sid, 'A mentor has been proposed for you. Please accept or decline.');
  return null;
}
function scoreBar(total) { return `<span class="scorebar"><span style="width:${total}%"></span></span> <b>${total}</b>/100`; }
/* Recommended pairs as a table; n = how many mentors to show per student. Call bindReco after inserting it. */
function recoHtml(d, n) {
  const rows = waitingStudents(d).map(st => {
    const recs = recommend(d, st.id, n);
    return recs.length ? recs.map((r, i) => `<tr>${i ? '' : `<td rowspan="${recs.length}"><b>${esc(st.name)}</b><br><span class="muted">${esc(topicsText(d.students[st.id].topics))}</span></td>`}
      <td>${esc(userName(d, r.mentorId))}<br><span class="muted">${esc(topicsText(d.mentors[r.mentorId].topics))}</span></td><td>${scoreBar(r.total)}${r.total < MIN_SCORE ? '<br><span class="muted">weak fit</span>' : ''}</td><td class="reasons">${r.reasons.map(esc).join('<br>')}</td>
      <td><button class="btn small" data-reco="${st.id}:${r.mentorId}">Propose</button></td></tr>`).join('')
      : `<tr><td><b>${esc(st.name)}</b></td><td colspan="4" class="muted">No eligible mentor right now (unverified or full).</td></tr>`;
  }).join('');
  return rows ? `<div class="table-wrap"><table><tr><th>Waiting student</th><th>Recommended mentor</th><th>Score</th><th>Why</th><th></th></tr>${rows}</table></div>` : '<p class="muted">Every student has an open match.</p>';
}
function bindReco(root, afterChange, by) {
  root.querySelectorAll('[data-reco]').forEach(b => b.onclick = () => {
    const [sid, mid] = b.dataset.reco.split(':').map(Number), x = load(), err = proposeMatch(x, sid, mid, 'Recommended by the platform', by);
    if (err) return toast(err); save(x); toast('Match proposed. Both people were notified.'); afterChange();
  });
}
