import { createRouter, createWebHashHistory } from 'vue-router';
import { HOME } from '../config/constants';
import { session, startSession } from '../services/auth';
import { db, commit } from '../services/db';
import { sendReminders } from '../services/checkins';

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
  if (import.meta.env.DEV && to.query.demo) {
    const { applyDemoState } = await import('../dev/demoStates');
    applyDemoState(db, to.query.demo);
    commit();
  }
  if (import.meta.env.DEV && to.query.as && !session.value) {
    const user = db.users.find(u => u.id === DEMO_USER[to.query.as]);
    if (user) startSession(user);
  }
  if (sendReminders(db)) commit();
  const role = session.value && session.value.role;
  if (to.meta.guest && role) return HOME[role];
  if (to.meta.role) {
    if (!role) return '/login';
    if (to.meta.role !== role) return HOME[role];
  }
  return true;
});

export default router;
