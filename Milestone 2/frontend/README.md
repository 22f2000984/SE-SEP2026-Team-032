# Team 032 – Mentor Connect: Milestone 2 Frontend (Vue 3)

Student Mentoring and Career Support Platform. A Vue 3 + Vite frontend with sample data kept in the browser. There is no backend yet: the data layer is one folder (`src/services`) that the real APIs replace in Sprint 1.

## Run
You need Node.js 18 or newer.

```bash
cd frontend
npm install
npm run dev        # opens the app at http://localhost:5173
```

Other commands:

| Command | What it does |
|---|---|
| `npm run build` | Builds the app into `dist/` (what a host such as Vercel serves) |
| `npm run preview` | Serves the built app locally |
| `npm test` | Runs the unit tests (matching, Smart Match, match flow, weekly check-ins, login and profiles) |

Page addresses use `#`, for example `/#/admin/matches`, so the app works on any static host without extra settings.

## Demo accounts (password `demo123`)
| Role | Email |
|---|---|
| Student | `asha@student.test` |
| Mentor | `meera@mentor.test` |
| Admin | `admin@client.test` |

Use "Reset demo data" on the log in page to start over.

## Pages
| Address | Role | Purpose |
|---|---|---|
| `/#/login`, `/#/register` | everyone | Log in, create an account |
| `/#/student` | student | Dashboard, match status, notifications |
| `/#/student/profile` | student | Goals, skills, wanted topics, format, duration, availability, free text about needs |
| `/#/student/mentor` | student | Status and next step, proposed mentor to accept or decline, feedback, concerns |
| `/#/student/checkins` | student | Weekly check-ins: mentor's email, state of each week, the form for the week that is due |
| `/#/mentor` | mentor | Accept or decline match requests, active mentees |
| `/#/mentor/profile` | mentor | Background, topics, maximum students, free text about what they offer, availability slots |
| `/#/mentor/checkins` | mentor | Weekly check-ins for each active mentee |
| `/#/admin` | admin | What needs attention, recommended matches, and tabs for concerns, feedback, mentor capacity and recent activity |
| `/#/admin/students` | admin | View, search and filter student profiles and responses |
| `/#/admin/mentors` | admin | Review, edit and verify mentor profiles and availability |
| `/#/admin/matches` | admin | Recommended matches with Smart Match scores and reasons, compare student and mentor, propose, confirm or cancel, change status |
| `/#/admin/pulse` | admin | Mentorship Pulse: check-ins that need review, active mentorships, emails sent |

A signed-in user who opens another role's address is sent back to their own dashboard.

## Workflow
The admin proposes a match and both the mentor and the student are notified. Each accepts or declines. Only when both have accepted can the admin confirm the match, which makes it active; the admin can cancel it instead. Statuses: proposed, active (confirmed by the admin), completed, cancelled. Students and mentors never browse each other.

## Smart Match and Mentorship Pulse (design preview)
Milestone 2 is a design, so the two AI features are shown with an **offline stand-in**. It has the same inputs and outputs as the AI agent that the backend calls in a later sprint, so the pages do not change when the agent is connected.

- **Smart Match.** The student and the mentor each write a free text (what I need, what I offer). Every student without a match is scored against every verified mentor who still has free places, out of 100, with a reason. The stand-in compares the wording of the two texts (60 points) and adds the rule score, topic overlap 70 and experience 30, scaled to 40 points. The rule score is shown next to it. The platform only recommends: the admin proposes. Each mentor sets a maximum number of students; a proposal over that limit is refused.
- **Mentorship Pulse.** When the admin confirms a match, each person gets an email with the other's address (recorded in the Emails list, not sent), and a check-in is created for each week of the mentorship (1 month = 4 weeks, 3 months = 12, 6 months = 24). Each person answers a rating and a comment. The stand-in review gives a verdict (on track, watch, needs attention) and a reason; a rating of 2 or less, or an unanswered check-in, is flagged. A week without a session is not flagged. The admin sees the flagged ones on the Pulse page and marks them reviewed.

## Code structure
```
src/
  main.js, App.vue          start-up and layout switch
  router/                   routes and role guard
  layouts/                  AppLayout (header, page, footer), AuthLayout (log in and register)
  views/                    one file per page: auth/, student/, mentor/, admin/
  components/common/        header, badges, bars, topic picker, toast, notification list
  components/match/         recommendation table, student and mentor comparison
  components/checkin/       the weekly check-in panel
  services/                 data layer: db, auth, matching, smartMatch, matches, profiles, checkins, pulseReview, feedback, notifications
  config/constants.js       topics, formats, statuses, score weights, check-in rules, navigation
  data/seed.js              sample data
  composables/              useDb, useToast
  assets/styles/            tokens, base, layout, components, auth
tests/                      unit tests for the services
```
Views only talk to `src/services`. In Sprint 1 those functions call the backend APIs, and the views stay as they are.

## Limitations
Sample data is stored in the browser (localStorage), so each visitor sees their own copy. There is no backend, real authentication or email. Passwords are stored in plain text for the demo only. Role checks hide pages in the browser; the backend must enforce them.
