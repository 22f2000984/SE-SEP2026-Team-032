/* Shared helpers for the Milestone 2 prototype.
   All data is sample data kept in the browser (localStorage). There is no backend. */
const DB_KEY = 't32_data', USER_KEY = 't32_user';
const STATUSES = ['proposed', 'active', 'completed', 'cancelled'];
const NEXT = { proposed: ['active', 'cancelled'], active: ['completed', 'cancelled'], completed: [], cancelled: [] };
const NAVS = {
  student: [['student.html', 'Dashboard'], ['student-profile.html', 'My Profile'], ['student-mentor.html', 'My Mentor']],
  mentor: [['mentor.html', 'Dashboard'], ['mentor-profile.html', 'My Profile']],
  admin: [['admin.html', 'Overview'], ['admin-mentors.html', 'Mentors'], ['admin-matches.html', 'Matches']]
};
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
      1: { programme: 'Diploma', goals: 'Move into data analytics', skills: 'Python, SQL', preferences: 'Weekend calls', availability: 'Sat-Sun evenings', readiness: 'unknown' },
      2: { programme: 'Foundation', goals: '', skills: '', preferences: '', availability: '', readiness: 'unknown' }
    },
    mentors: {
      3: { qualifications: 'PhD, Data Science', experience: 12, expertise: 'Analytics, career transitions', bio: 'Leads an analytics team and mentors early-career students.', status: 'verified' },
      4: { qualifications: 'B.Tech', experience: 5, expertise: 'Web development', bio: '', status: 'pending' }
    },
    slots: [{ id: 1, mentorId: 3, day: 'Saturday', start: '18:00', end: '20:00' }],
    matches: [{ id: 1, studentId: 1, mentorId: 3, status: 'proposed', notes: 'Goal fit: analytics', proposedAt: daysAgo(5), log: [{ from: '-', to: 'proposed', at: daysAgo(5), by: 'Coordinator' }] }],
    concerns: [], feedback: [],
    notifications: [{ id: 1, userId: 3, text: 'A new student match is waiting for your response.', at: daysAgo(5), read: false }]
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
function pill(s) { return `<span class="pill ${esc(s)}">${esc(s)}</span>`; }
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
function setStatus(d, m, to, by) {
  m.log.push({ from: m.status, to, at: new Date().toISOString(), by });
  m.status = to;
  const sName = userName(d, m.studentId), mName = userName(d, m.mentorId);
  notify(d, m.studentId, `Your mentoring match with ${mName} is now ${to}.`);
  notify(d, m.mentorId, `Your match with ${sName} is now ${to}.`);
  d.users.filter(u => u.role === 'admin').forEach(a => notify(d, a.id, `Match ${sName} / ${mName} is now ${to}.`));
}

/* Demo shortcut used for screenshots: page.html?as=student|mentor|admin signs in as the sample user. */
(function () {
  const as = new URLSearchParams(location.search).get('as'), ids = { student: 1, mentor: 3, admin: 5 };
  if (!as || !ids[as] || me()) return;
  const u = load().users.find(x => x.id === ids[as]);
  try { sessionStorage.setItem(USER_KEY, JSON.stringify({ id: u.id, name: u.name, role: u.role })); } catch (e) {}
})();
