/* Shared helpers for the Milestone 2 prototype.
   All data is sample data kept in the browser (localStorage). There is no backend. */
const DB_KEY = 't32_data_v2', USER_KEY = 't32_user';
const STATUSES = ['proposed', 'active', 'completed', 'cancelled'];
const NEXT = { proposed: ['active', 'cancelled'], active: ['completed', 'cancelled'], completed: [], cancelled: [] };
const NAVS = {
  student: [['student.html', 'Dashboard'], ['student-profile.html', 'My Profile'], ['student-mentor.html', 'My Mentor']],
  mentor: [['mentor.html', 'Dashboard'], ['mentor-profile.html', 'My Profile']],
  admin: [['admin.html', 'Overview'], ['admin-students.html', 'Students'], ['admin-mentors.html', 'Mentors'], ['admin-matches.html', 'Matches']]
};
const FORMATS = ['No preference', 'Video call', 'Phone call', 'Messaging'], DURATIONS = ['Not sure yet', '1 month', '3 months', '6 months'];
const NEXT_STEP = { proposed: 'Accept or decline the proposed match. The coordinator confirms it once both the mentor and the student have accepted.', active: 'Agree the first session with your mentor. Share feedback or a concern at any time.', completed: 'Mentoring has finished. Please leave feedback if you have not yet.', cancelled: 'This match has ended. The coordinator will arrange a new one.' };
const daysAgo = n => new Date(Date.now() - n * 864e5).toISOString();

function seed() {
  return {
    nextId: 100,
    users: [
      { id: 1, email: 'asha@student.test', password: 'demo123', name: 'Asha Verma', role: 'student' },
      { id: 2, email: 'rohan@student.test', password: 'demo123', name: 'Rohan Das', role: 'student' },
      { id: 3, email: 'meera@mentor.test', password: 'demo123', name: 'Dr. Meera Iyer', role: 'mentor' },
      { id: 4, email: 'karan@mentor.test', password: 'demo123', name: 'Karan Shah', role: 'mentor' },
      { id: 5, email: 'admin@client.test', password: 'demo123', name: 'Coordinator', role: 'admin' }
    ],
    students: {
      1: { programme: 'Diploma', goals: 'Move into data analytics', skills: 'Python, SQL', expertise: 'Analytics, career transitions', format: 'Video call', duration: '3 months', preferences: 'Weekend calls', availability: 'Sat-Sun evenings' },
      2: { programme: 'Foundation', goals: '', skills: '', expertise: '', format: 'No preference', duration: 'Not sure yet', preferences: '', availability: '' }
    },
    mentors: {
      3: { qualifications: 'PhD, Data Science', experience: 12, expertise: 'Analytics, career transitions', bio: 'Leads an analytics team and mentors early-career students.', status: 'verified' },
      4: { qualifications: 'B.Tech', experience: 5, expertise: 'Web development', bio: '', status: 'pending' }
    },
    slots: [{ id: 1, mentorId: 3, day: 'Saturday', start: '18:00', end: '20:00' }],
    matches: [{ id: 1, studentId: 1, mentorId: 3, status: 'proposed', notes: 'Goal fit: analytics', proposedAt: daysAgo(5), mentorResponse: 'pending', studentResponse: 'pending', mentorRespondedAt: null, studentRespondedAt: null, confirmedAt: null, log: [{ from: '-', to: 'proposed', at: daysAgo(5), by: 'Coordinator' }] }],
    concerns: [], feedback: [],
    notifications: [{ id: 1, userId: 3, text: 'A new student match is waiting for your response.', at: daysAgo(5), read: false }, { id: 2, userId: 1, text: 'A mentor has been proposed for you. Please accept or decline.', at: daysAgo(5), read: false }]
  };
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
    `<header><a class="brand" href="${NAVS[u.role][0][0]}">IITM · MENTOR CONNECT</a><nav class="nav">${links}<span class="who">${esc(u.name)} (${u.role})</span><a href="#" id="logout">Log out</a></nav></header>`);
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
/* who is 'mentor' or 'student'; answer is 'accepted' or 'declined'. The coordinator is told, and when both accept, can confirm. */
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

function slotText(d, mid) { const t = d.slots.filter(x => x.mentorId === mid).map(x => `${x.day} ${x.start}-${x.end}`).join(', '); return t || 'no slots added'; }
