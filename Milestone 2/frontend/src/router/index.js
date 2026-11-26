import { createRouter, createWebHashHistory } from 'vue-router';
import { HOME } from '../config/constants';
import { session, startSession, logout } from '../services/auth';
import { API_ON } from '../services/api';
import { syncDb } from '../services/remote';
import { db, commit } from '../services/db';
import { sendReminders } from '../services/checkins';
import { mentorComplete } from '../services/profiles';

const routes = [
  { path: '/', redirect: () => (session.value ? HOME[session.value.role] : '/login') },
  { path: '/login', component: () => import('../views/auth/LoginView.vue'), meta: { layout: 'auth', guest: true } },
  { path: '/register', component: () => import('../views/auth/RegisterView.vue'), meta: { layout: 'auth', guest: true } },

  { path: '/student', component: () => import('../views/student/StudentDashboard.vue'), meta: { role: 'student' } },
  { path: '/student/profile', component: () => import('../views/student/StudentProfile.vue'), meta: { role: 'student' } },
  { path: '/student/mentor', component: () => import('../views/student/StudentMentor.vue'), meta: { role: 'student' } },

  { path: '/student/checkins', component: () => import('../views/student/StudentCheckIns.vue'), meta: { role: 'student' } },

  { path: '/mentor', component: () => import('../views/mentor/MentorDashboard.vue'), meta: { role: 'mentor' } },
  { path: '/mentor/profile', component: () => import('../views/mentor/MentorProfile.vue'), meta: { role: 'mentor' } },

  { path: '/mentor/checkins', component: () => import('../views/mentor/MentorCheckIns.vue'), meta: { role: 'mentor' } },

  { path: '/admin', component: () => import('../views/admin/AdminOverview.vue'), meta: { role: 'admin' } },
  { path: '/admin/students', component: () => import('../views/admin/AdminStudents.vue'), meta: { role: 'admin' } },
  { path: '/admin/mentors', component: () => import('../views/admin/AdminMentors.vue'), meta: { role: 'admin' } },
  { path: '/admin/matches', component: () => import('../views/admin/AdminMatches.vue'), meta: { role: 'admin' } },

  { path: '/admin/pulse', component: () => import('../views/admin/AdminPulse.vue'), meta: { role: 'admin' } },

  { path: '/:pathMatch(.*)*', redirect: '/' }
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 })
});

/* Development-only shortcuts for screenshots, removed from the production build:
   /#/admin?as=admin signs in as the sample user, and ?demo=ready|active|mentor-accepted sets up a known state. */
const DEMO_USER = { student: 1, mentor: 3, admin: 5 };

router.beforeEach(async to => {
  if (API_ON) {
    /* With the backend on, the data comes from the API: refresh it on every page change. A wrong or expired token means log in again. */
    if (session.value) {
      try {
        await syncDb();
      } catch (e) {
        /* Log in again when the token is refused, or when there is no data to show (the pages need it). */
        const noData = !db.users.some(u => u.id === session.value.id);
        if (e.status === 401 || e.status === 403 || noData) { logout(); return '/login'; }
      }
    }
  } else if (import.meta.env.DEV && to.query.demo) {
    const { applyDemoState } = await import('../dev/demoStates');
    applyDemoState(db, to.query.demo);
    commit();
  }
  if (!API_ON && import.meta.env.DEV && to.query.as && !session.value) {
    const user = db.users.find(u => u.id === DEMO_USER[to.query.as]);
    if (user) startSession(user);
  }
  if (!API_ON && sendReminders(db)) commit();
  const role = session.value && session.value.role;
  if (to.meta.guest && role) return HOME[role];
  if (to.meta.role) {
    if (!role) return '/login';
    if (to.meta.role !== role) return HOME[role];
    /* A new mentor must finish the profile first; only then does the admin see them for verification. */
    const me = db.mentors[session.value.id];
    if (role === 'mentor' && me && me.status === 'pending' && !mentorComplete(db, session.value.id) && to.path !== '/mentor/profile') return '/mentor/profile';
  }
  return true;
});

export default router;
