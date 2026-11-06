import { describe, it, expect } from 'vitest';
import { createSeed } from '../src/data/seed';
import { keywords, smartScore, recommendSmart } from '../src/services/smartMatch';
import { saveMentorProfile, adminEditMentor } from '../src/services/profiles';

describe('Smart Match (offline stand-in for the AI agent)', () => {
  it('keeps the meaningful words and drops filler words', () => {
    const words = [...keywords('I want to move into data analytics and need help with SQL').values()];
    expect(words).toEqual(['move', 'data', 'analytics', 'sql']);
  });

  it('scores a pair out of 100 with a reason that names the shared words', () => {
    const d = createSeed();
    const s = smartScore(d, 6, 7);
    expect(s.total).toBeGreaterThan(90);
    expect(s.total).toBeLessThanOrEqual(100);
    expect(s.reason).toMatch(/Both describe: .*product/);
    expect(s.ruleTotal).toBe(94);
  });

  it('gives a low score when the texts and topics do not fit', () => {
    const d = createSeed();
    expect(smartScore(d, 6, 3).total).toBeLessThan(40);
  });

  it('ranks only eligible mentors, best first', () => {
    const d = createSeed();
    const recs = recommendSmart(d, 2, 5);
    expect(recs.map(r => r.mentorId)).not.toContain(4);
    expect(recs[0].total).toBeGreaterThanOrEqual(recs[recs.length - 1].total);
  });

  it('does not wipe the mentor text when the admin edits the profile', () => {
    const d = createSeed();
    const before = d.mentors[7].skillsText;
    expect(adminEditMentor(d, 7, { qualifications: 'MBA', experience: 9, topics: ['Product Management'], maxStudents: 2, bio: 'x' })).toBeNull();
    expect(d.mentors[7].skillsText).toBe(before);
    expect(saveMentorProfile(d, 7, { qualifications: 'MBA', experience: 9, topics: ['Product Management'], maxStudents: 2, bio: 'x', skillsText: 'new text' })).toBeNull();
    expect(d.mentors[7].skillsText).toBe('new text');
  });

  it('refuses a free text that is too long', () => {
    const d = createSeed();
    expect(saveMentorProfile(d, 7, { qualifications: 'MBA', topics: ['Cloud and DevOps'], maxStudents: 2, skillsText: 'a'.repeat(801) })).toMatch(/800/);
  });
});
