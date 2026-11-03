/* Student and mentor profiles: validation and saving. Each function returns an error message or null. */
import { MAX_CAPACITY } from '../config/constants';
import { nextId } from './ids';
import { notify } from './notifications';
import { used } from './matching';

export function saveStudentProfile(d, studentId, f) {
  const goals = (f.goals || '').trim(), programme = (f.programme || '').trim();
  if (!programme || !goals) return 'Programme level and career goals are required.';
  if (goals.length > 500) return 'Career goals must be 500 characters or fewer.';
  if (!f.topics.length) return 'Choose at least one topic so the admin can match you.';
  Object.assign(d.students[studentId], {
    programme, goals, skills: (f.skills || '').trim(), topics: [...f.topics], format: f.format, duration: f.duration,
    availability: (f.availability || '').trim(), preferences: (f.preferences || '').trim()
  });
  return null;
}

/* Shared by the mentor (own profile) and the admin (editing a mentor). */
export function validateMentor(d, mentorId, f) {
  if (!(f.qualifications || '').trim() || !f.topics.length) return 'Qualifications and at least one topic are required.';
  const mx = Number(f.maxStudents);
  if (!(mx >= 1 && mx <= MAX_CAPACITY)) return `Maximum students must be between 1 and ${MAX_CAPACITY}.`;
  if (mx < used(d, mentorId)) return `This mentor already has ${used(d, mentorId)} open matches, so the maximum cannot be lower.`;
  return null;
}
export function saveMentorProfile(d, mentorId, f) {
  const err = validateMentor(d, mentorId, f);
  if (err) return err;
  Object.assign(d.mentors[mentorId], {
    qualifications: f.qualifications.trim(), experience: Number(f.experience) || 0, topics: [...f.topics],
    maxStudents: Number(f.maxStudents), bio: (f.bio || '').trim()
  });
  return null;
}
export function adminEditMentor(d, mentorId, f) {
  const err = saveMentorProfile(d, mentorId, f);
  if (!err) notify(d, mentorId, 'The admin updated your mentor profile.');
  return err;
}
export function verifyMentor(d, mentorId) {
  d.mentors[mentorId].status = 'verified';
  notify(d, mentorId, 'Your mentor profile has been verified.');
}

export function addSlot(d, mentorId, day, start, end) {
  if (!start || !end || end <= start) return 'End time must be after start time.';
  d.slots.push({ id: nextId(d), mentorId, day, start, end });
  return null;
}
export function removeSlot(d, slotId) {
  d.slots = d.slots.filter(s => s.id !== slotId);
}
export function slotText(d, mentorId) {
  const t = d.slots.filter(x => x.mentorId === mentorId).map(x => `${x.day} ${x.start}-${x.end}`).join(', ');
  return t || 'no slots added';
}
