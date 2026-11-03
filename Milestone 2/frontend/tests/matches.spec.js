import { describe, it, expect } from 'vitest';
import { createSeed } from '../src/data/seed';
import { NEXT } from '../src/config/constants';
import { respond, setStatus, bothAccepted, proposeMatch } from '../src/services/matches';

describe('match flow', () => {
  it('only allows the planned status changes', () => {
    expect(NEXT.proposed).toEqual(['active', 'cancelled']);
    expect(NEXT.active).toEqual(['completed', 'cancelled']);
    expect(NEXT.completed).toEqual([]);
    expect(NEXT.cancelled).toEqual([]);
  });

  it('starts proposed with both answers pending', () => {
    const m = createSeed().matches[0];
    expect(m.status).toBe('proposed');
    expect([m.mentorResponse, m.studentResponse]).toEqual(['pending', 'pending']);
  });

  it('cannot be confirmed until both sides accept', () => {
    const d = createSeed(), m = d.matches[0];
    expect(setStatus(d, m, 'active', 'Admin')).toBe(false);
    respond(d, m, 'mentor', 'accepted');
    expect(m.status).toBe('proposed');
    expect(setStatus(d, m, 'active', 'Admin')).toBe(false);
    respond(d, m, 'student', 'accepted');
    expect(bothAccepted(m)).toBe(true);
    expect(d.notifications.some(n => n.userId === 5 && /ready for you to confirm/.test(n.text))).toBe(true);
    expect(setStatus(d, m, 'active', 'Admin')).toBe(true);
    expect(m.status).toBe('active');
    expect(m.confirmedAt).toBeTruthy();
    expect(m.log.map(l => l.to)).toEqual(['proposed', 'active']);
  });

  it('tells the student and the mentor when the admin confirms', () => {
    const d = createSeed(), m = d.matches[0];
    respond(d, m, 'mentor', 'accepted');
    respond(d, m, 'student', 'accepted');
    setStatus(d, m, 'active', 'Admin');
    expect(d.notifications.some(n => n.userId === 1 && /now active/.test(n.text) && /Next step/.test(n.text))).toBe(true);
    expect(d.notifications.some(n => n.userId === 3 && /now active/.test(n.text))).toBe(true);
  });

  it('lets the admin cancel a declined proposal but never confirm it', () => {
    const d = createSeed(), m = d.matches[0];
    respond(d, m, 'student', 'declined');
    expect(setStatus(d, m, 'active', 'Admin')).toBe(false);
    expect(setStatus(d, m, 'cancelled', 'Admin')).toBe(true);
    expect(m.status).toBe('cancelled');
  });

  it('notifies both the mentor and the student when a match is proposed, and saves the score', () => {
    const d = createSeed();
    expect(proposeMatch(d, 6, 7, 'test', 'Admin')).toBeNull();
    const m = d.matches[1];
    expect(m.matchScore).toBe(94);
    expect(d.notifications.some(n => n.userId === 6 && /mentor has been proposed/.test(n.text))).toBe(true);
    expect(d.notifications.some(n => n.userId === 7 && /waiting for your response/.test(n.text))).toBe(true);
  });
});
