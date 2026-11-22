import { describe, it, expect, beforeEach } from 'vitest';
import { createSeed } from '../src/data/seed';
import { mentorComplete, onAdminList } from '../src/services/profiles';
import { peopleSummary } from '../src/services/analytics';

let d;
beforeEach(() => { d = createSeed(); });

describe('mentor onboarding', () => {
  it('a mentor with qualifications, bio, topic and a slot is complete', () => {
    expect(mentorComplete(d, 4)).toBe(true);
  });

  it('a mentor without a bio, a topic or a slot is not complete', () => {
    d.mentors[4].bio = '';
    expect(mentorComplete(d, 4)).toBe(false);
    d.mentors[4].bio = 'ok'; d.slots = d.slots.filter(s => s.mentorId !== 4);
    expect(mentorComplete(d, 4)).toBe(false);
  });

  it('an incomplete pending mentor is hidden from the admin and not counted', () => {
    d.mentors[4].bio = '';
    expect(onAdminList(d, 4)).toBe(false);
    expect(peopleSummary(d).pending).toBe(0);
  });

  it('a verified mentor stays on the admin list', () => {
    d.slots = d.slots.filter(s => s.mentorId !== 3);
    expect(onAdminList(d, 3)).toBe(true);
  });
});
