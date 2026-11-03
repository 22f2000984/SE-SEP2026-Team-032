/* Fixed lists and rules used across the app. Changing a value here changes it everywhere. */

export const TOPICS = [
  'Data Science', 'Web Development', 'Career Switching', 'Interview Preparation',
  'Product Management', 'Higher Studies', 'Entrepreneurship', 'Cloud and DevOps'
];
export const FORMATS = ['No preference', 'Video call', 'Phone call', 'Messaging'];
export const DURATIONS = ['Not sure yet', '1 month', '3 months', '6 months'];
export const WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

/* Match status and the changes the admin may make after a match is proposed. */
export const STATUSES = ['proposed', 'active', 'completed', 'cancelled'];
export const NEXT = { proposed: ['active', 'cancelled'], active: ['completed', 'cancelled'], completed: [], cancelled: [] };
export const NEXT_STEP = {
  proposed: 'Accept or decline the proposed match. The admin confirms it once both the mentor and the student have accepted.',
  active: 'Agree the first session with your mentor. Share feedback or a concern at any time.',
  completed: 'Mentoring has finished. Please leave feedback if you have not yet.',
  cancelled: 'This match has ended. The admin will arrange a new one.'
};

/* Matching: score out of 100 from topic overlap and mentor experience only. */
export const WEIGHTS = { topics: 70, experience: 30 };
export const MIN_SCORE = 40;
export const EXPERIENCE_CAP_YEARS = 10;
export const DEFAULT_CAPACITY = 3;
export const MAX_CAPACITY = 10;

/* Navigation per role. */
export const HOME = { student: '/student', mentor: '/mentor', admin: '/admin' };
export const NAV = {
  student: [
    { to: '/student', label: 'Dashboard', exact: true },
    { to: '/student/profile', label: 'My Profile' },
    { to: '/student/mentor', label: 'My Mentor' }
  ],
  mentor: [
    { to: '/mentor', label: 'Dashboard', exact: true },
    { to: '/mentor/profile', label: 'My Profile' }
  ],
  admin: [
    { to: '/admin', label: 'Overview', exact: true },
    { to: '/admin/students', label: 'Students' },
    { to: '/admin/mentors', label: 'Mentors' },
    { to: '/admin/matches', label: 'Matches' }
  ]
};
