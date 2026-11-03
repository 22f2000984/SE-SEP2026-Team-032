import { describe, it, expect } from 'vitest';
import { createSeed } from '../src/data/seed';
import { eligible, scoreMatch, recommend, waitingStudents, used, maxOf } from '../src/services/matching';
import { proposeMatch } from '../src/services/matches';

describe('scoring', () => {
  it('scores only topics (70) and experience (30)', () => {
    const d = createSeed();
    const s = scoreMatch(d, 6, 7); // Neha with Priya
    expect(s.parts).toEqual({ topics: 70, experience: 24 });
    expect(s.total).toBe(94);
  });
  it('gives the seed match Asha / Dr. Meera 100 points', () => {
    expect(createSeed().matches[0].matchScore).toBe(100);
  });
  it('ranks mentors for Rohan: Priya 59, then Dr. Meera 30', () => {
    const r = recommend(createSeed(), 2, 3);
    expect(r.map(x => [x.mentorId, x.total])).toEqual([[7, 59], [3, 30]]);
  });
  it('gives no points for free places', () => {
    const d = createSeed();
    const before = scoreMatch(d, 6, 7).total;
    proposeMatch(d, 2, 7, '', 'Admin'); // Priya now has 1 of 2 places used
    expect(scoreMatch(d, 6, 7).total).toBe(before);
  });
});

describe('who may be proposed', () => {
  it('refuses an unverified mentor', () => {
    expect(eligible(createSeed(), 2, 4)).toBe('The mentor is not verified yet.');
  });
  it('refuses a student who already has an open match', () => {
    expect(eligible(createSeed(), 1, 7)).toBe('This student already has an open match.');
  });
  it('lists the students waiting for a match', () => {
    expect(waitingStudents(createSeed()).map(u => u.id)).toEqual([2, 6]);
  });
  it('refuses a mentor who is full and frees the place when a match is cancelled', () => {
    const d = createSeed();
    expect(proposeMatch(d, 6, 7, '', 'Admin')).toBeNull();
    expect(proposeMatch(d, 2, 7, '', 'Admin')).toBeNull();
    expect(used(d, 7)).toBe(2);
    expect(maxOf(d, 7)).toBe(2);
    d.users.push({ id: 90, role: 'student', name: 'X' });
    d.students[90] = { topics: ['Product Management'] };
    expect(eligible(d, 90, 7)).toBe('This mentor has no free places.');
    expect(recommend(d, 90, 3).every(r => r.mentorId !== 7)).toBe(true);
    d.matches.find(m => m.studentId === 6).status = 'cancelled';
    expect(eligible(d, 90, 7)).toBeNull();
  });
});
