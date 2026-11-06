import { describe, it, expect } from 'vitest';
import { createSeed } from '../src/data/seed';
import { respond, setStatus } from '../src/services/matches';
import { reviewCheckIn } from '../src/services/pulseReview';
import { weeksFor, checkInsOf, stateOf, submitCheckIn, sendReminders, flagged, markReviewed, toAnswer } from '../src/services/checkins';

/* Moves the calendar forward by n weeks, as if time had passed. */
function weeksPass(d, n) {
  d.matches.filter(m => m.status === 'active').forEach(m => {
    checkInsOf(d, m.id).forEach(c => { c.dueAt = new Date(new Date(c.dueAt).getTime() - n * 7 * 864e5).toISOString(); });
  });
}

function activeSeed() {
  const d = createSeed(), m = d.matches[0];
  respond(d, m, 'mentor', 'accepted');
  respond(d, m, 'student', 'accepted');
  setStatus(d, m, 'active', 'Admin');
  return { d, m };
}

describe('weekly check-ins (Mentorship Pulse)', () => {
  it('has one check-in per week for each side', () => {
    expect([weeksFor('1 month'), weeksFor('3 months'), weeksFor('6 months'), weeksFor('Not sure yet')]).toEqual([4, 12, 24, 4]);
    const { d, m } = activeSeed();
    expect(d.students[1].duration).toBe('3 months');
    expect(checkInsOf(d, m.id, 'student')).toHaveLength(12);
    expect(checkInsOf(d, m.id, 'mentor')).toHaveLength(12);
  });

  it('emails both people each other\'s address when the match becomes active', () => {
    const { d } = activeSeed();
    expect(d.notifications.some(n => n.email && n.userId === 1 && /meera@mentor\.test/.test(n.text))).toBe(true);
    expect(d.notifications.some(n => n.email && n.userId === 3 && /asha@student\.test/.test(n.text))).toBe(true);
  });

  it('creates nothing before the match is confirmed', () => {
    expect(createSeed().checkins).toEqual([]);
  });

  it('becomes due after a week, overdue after the grace period', () => {
    const { d, m } = activeSeed();
    const c = checkInsOf(d, m.id, 'student')[0], t = new Date(c.dueAt).getTime();
    expect(stateOf(c, t - 1)).toBe('upcoming');
    expect(stateOf(c, t + 1)).toBe('due');
    expect(stateOf(c, t + 3 * 864e5)).toBe('overdue');
  });

  it('sends one reminder email per due check-in, once', () => {
    const { d } = activeSeed();
    expect(sendReminders(d)).toBe(0);
    weeksPass(d, 1);
    expect(sendReminders(d)).toBe(2);
    expect(sendReminders(d)).toBe(0);
    expect(d.notifications.filter(n => n.email && /Reminder/.test(n.text))).toHaveLength(2);
    expect(toAnswer(d, 1, 'student')).toHaveLength(1);
  });

  it('flags a poor answer for the admin and notifies them', () => {
    const { d, m } = activeSeed();
    weeksPass(d, 1);
    const c = checkInsOf(d, m.id, 'student')[0];
    expect(submitCheckIn(d, c.id, { rating: 2, comment: 'The mentor cancelled and is hard to reach' })).toBeNull();
    expect(c.review.verdict).toBe('needs attention');
    expect(flagged(d)).toContain(c);
    expect(d.notifications.some(n => n.userId === 5 && /Mentorship Pulse/.test(n.text))).toBe(true);
    markReviewed(d, c.id, 'Called both');
    expect(flagged(d)).not.toContain(c);
  });

  it('does not flag a good answer', () => {
    const { d, m } = activeSeed();
    weeksPass(d, 1);
    const c = checkInsOf(d, m.id, 'mentor')[0];
    submitCheckIn(d, c.id, { rating: 5, comment: 'Great progress.' });
    expect(c.review.verdict).toBe('on track');
    expect(flagged(d)).toHaveLength(0);
  });

  it('flags a check-in that was never answered', () => {
    const { d } = activeSeed();
    weeksPass(d, 2);
    expect(flagged(d).length).toBeGreaterThan(0);
    const c = flagged(d)[0];
    markReviewed(d, c.id, '');
    expect(flagged(d)).not.toContain(c);
  });

  it('needs a rating', () => {
    const { d, m } = activeSeed();
    const c = checkInsOf(d, m.id, 'student')[0];
    expect(submitCheckIn(d, c.id, { rating: 0 })).toMatch(/rating/);
    expect(c.submittedAt).toBeNull();
    expect(submitCheckIn(d, c.id, { rating: 4 })).toBeNull();
    expect(c.submittedAt).toBeTruthy();
  });
});

describe('review rules', () => {
  it('maps ratings and comments to a verdict', () => {
    expect(reviewCheckIn({ rating: 5, comment: '' }).verdict).toBe('on track');
    expect(reviewCheckIn({ rating: 3, comment: '' }).verdict).toBe('watch');
    expect(reviewCheckIn({ rating: 5, comment: 'Sessions clash with exams' }).verdict).toBe('watch');
    expect(reviewCheckIn({ rating: 1, comment: '' }).verdict).toBe('needs attention');
    expect(reviewCheckIn({ rating: 5, comment: 'Skipped this week by agreement' }).verdict).toBe('on track');
  });
});
