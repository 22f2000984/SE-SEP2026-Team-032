import { describe, it, expect } from 'vitest';
import { createSeed } from '../src/data/seed';
import { login, register } from '../src/services/auth';
import { saveStudentProfile, saveMentorProfile, addSlot } from '../src/services/profiles';

describe('login and registration', () => {
  it('accepts the demo accounts and rejects wrong passwords', () => {
    const d = createSeed();
    expect(login(d, 'ASHA@student.test', 'demo123').role).toBe('student');
    expect(login(d, 'asha@student.test', 'wrong')).toBeNull();
  });
  it('checks name, email, password and duplicates', () => {
    const d = createSeed();
    expect(register(d, { role: 'student', name: '', email: 'a@b.co', password: 'secret1' })).toBe('Enter your name.');
    expect(register(d, { role: 'student', name: 'A', email: 'nope', password: 'secret1' })).toBe('Enter a valid email.');
    expect(register(d, { role: 'student', name: 'A', email: 'a@b.co', password: '123' })).toBe('Password needs at least 6 characters.');
    expect(register(d, { role: 'student', name: 'A', email: 'asha@student.test', password: 'secret1' })).toBe('This email is already registered.');
  });
  it('creates a pending mentor and tells the admin', () => {
    const d = createSeed();
    expect(register(d, { role: 'mentor', name: 'New Mentor', email: 'new@m.test', password: 'secret1' })).toBeNull();
    const user = d.users.find(u => u.email === 'new@m.test');
    expect(d.mentors[user.id].status).toBe('pending');
    expect(d.notifications.some(n => n.userId === 5 && /New mentor registered/.test(n.text))).toBe(true);
  });
});

describe('profiles', () => {
  it('needs programme, goals and at least one topic from a student', () => {
    const d = createSeed(), base = { programme: 'Diploma', goals: 'g', skills: '', topics: ['Data Science'], format: 'Video call', duration: '3 months', availability: '', preferences: '' };
    expect(saveStudentProfile(d, 1, { ...base, goals: '' })).toBe('Programme level and career goals are required.');
    expect(saveStudentProfile(d, 1, { ...base, goals: 'x'.repeat(501) })).toBe('Career goals must be 500 characters or fewer.');
    expect(saveStudentProfile(d, 1, { ...base, topics: [] })).toBe('Choose at least one topic so the admin can match you.');
    expect(saveStudentProfile(d, 1, base)).toBeNull();
  });
  it('keeps the maximum students between 1 and 10 and never below the open matches', () => {
    const d = createSeed(), base = { qualifications: 'PhD', experience: 12, topics: ['Data Science'], maxStudents: 3, bio: '' };
    expect(saveMentorProfile(d, 3, { ...base, maxStudents: 0 })).toMatch(/between 1 and 10/);
    expect(saveMentorProfile(d, 3, { ...base, maxStudents: 11 })).toMatch(/between 1 and 10/);
    expect(saveMentorProfile(d, 3, { ...base, topics: [] })).toBe('Qualifications and at least one topic are required.');
    expect(saveMentorProfile(d, 3, base)).toBeNull();
  });
  it('needs the end time to be after the start time', () => {
    const d = createSeed();
    expect(addSlot(d, 3, 'Monday', '18:00', '17:00')).toBe('End time must be after start time.');
    expect(addSlot(d, 3, 'Monday', '18:00', '19:00')).toBeNull();
  });
});
