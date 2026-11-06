import { describe, it, expect, beforeEach } from 'vitest';
import { createSeed } from '../src/data/seed';
import { respond, setStatus, proposeMatch } from '../src/services/matches';
import { checkInsOf, submitCheckIn } from '../src/services/checkins';
import { addFeedback } from '../src/services/feedback';
import { matchCounts, pulseSummary, feedbackSummary, capacitySummary, peopleSummary } from '../src/services/analytics';

let d;
const DAY = 864e5;
function activate(match) {
  respond(d, match, 'mentor', 'accepted');
  respond(d, match, 'student', 'accepted');
  setStatus(d, match, 'active', 'Admin');
}
/* Pretends the match was confirmed some days ago so that its check-ins fall due. */
function ageMatch(match, days) {
  match.confirmedAt = new Date(Date.now() - days * DAY).toISOString();
  checkInsOf(d, match.id).forEach(c => { c.dueAt = new Date(new Date(match.confirmedAt).getTime() + c.week * 7 * DAY).toISOString(); });
}

beforeEach(() => { d = createSeed(); });

describe('analytics', () => {
  it('counts matches by status', () => {
    expect(matchCounts(d)).toEqual([
      { status: 'proposed', count: 1 }, { status: 'active', count: 0 }, { status: 'completed', count: 0 }, { status: 'cancelled', count: 0 }
    ]);
    activate(d.matches[0]);
    expect(matchCounts(d).find(x => x.status === 'active').count).toBe(1);
  });

  it('counts students, mentors and those waiting', () => {
    expect(peopleSummary(d)).toEqual({ students: 3, waiting: 2, mentors: 3, verified: 2, pending: 1 });
  });

  it('has no check-in numbers before any week has passed', () => {
    activate(d.matches[0]);
    const p = pulseSummary(d);
    expect(p).toMatchObject({ asked: 0, answered: 0, responseRate: 0 });
  });

  it('summarises answered and unanswered check-ins and their verdicts', () => {
    activate(d.matches[0]);
    ageMatch(d.matches[0], 15);
    const [s1, m1] = [checkInsOf(d, 1, 'student')[0], checkInsOf(d, 1, 'mentor')[0]];
    submitCheckIn(d, s1.id, { rating: 5, comment: 'Great' });
    submitCheckIn(d, m1.id, { rating: 2, comment: 'Not responding' });
    const p = pulseSummary(d);
    expect(p.asked).toBe(4);
    expect(p.answered).toBe(2);
    expect(p.responseRate).toBe(50);
    expect(p.onTrack).toBe(1);
    expect(p.needsAttention).toBe(1);
    expect(p.unanswered).toBe(2);
  });

  it('averages the feedback and counts each rating', () => {
    expect(feedbackSummary(d)).toMatchObject({ total: 0, average: null });
    addFeedback(d, 1, 1, 5, '');
    addFeedback(d, 1, 3, 4, '');
    const f = feedbackSummary(d);
    expect(f.average).toBe(4.5);
    expect(f.counts.find(c => c.rating === 5).count).toBe(1);
  });

  it('reports the places in use across verified mentors', () => {
    expect(capacitySummary(d)).toMatchObject({ used: 1, places: 5, percent: 20 });
    expect(proposeMatch(d, 6, 7, '', 'Admin')).toBeNull();
    expect(capacitySummary(d).used).toBe(2);
  });
});
