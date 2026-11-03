/* Sample data for the prototype. In Sprint 1 this is replaced by the database behind the APIs. */
import { scoreMatch } from '../services/matching';

export function createSeed(now = Date.now()) {
  const daysAgo = n => new Date(now - n * 864e5).toISOString();
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
    matches: [{
      id: 1, studentId: 1, mentorId: 3, status: 'proposed', notes: 'Goal fit: analytics', proposedAt: daysAgo(5),
      mentorResponse: 'pending', studentResponse: 'pending', mentorRespondedAt: null, studentRespondedAt: null, confirmedAt: null,
      log: [{ from: '-', to: 'proposed', at: daysAgo(5), by: 'Admin' }]
    }],
    concerns: [],
    feedback: [],
    notifications: [
      { id: 1, userId: 3, text: 'A new student match is waiting for your response.', at: daysAgo(5), read: false },
      { id: 2, userId: 1, text: 'A mentor has been proposed for you. Please accept or decline.', at: daysAgo(5), read: false }
    ]
  };
  const sc = scoreMatch(d, 1, 3);
  d.matches[0].matchScore = sc.total;
  d.matches[0].scoreReasons = sc.reasons.join('; ');
  return d;
}
