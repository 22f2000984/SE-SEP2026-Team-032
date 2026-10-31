# Team 032 – Milestone 2 Frontend Prototype

Student Mentoring and Career Support Platform. Plain HTML, CSS and JavaScript. No install or build step.

## Run
1. Unzip the package and open the `frontend` folder.
2. Open `index.html` in Chrome, Edge or Firefox (double-click is enough).
3. Log in with a demo account (password `demo123`):
   - Student: `asha@student.test`
   - Mentor: `meera@mentor.test`
   - Coordinator: `admin@client.test`

## Pages
| Page | Role | Purpose |
|---|---|---|
| `index.html`, `register.html` | all | Log in, create an account |
| `student.html` | student | Dashboard, match status, notifications |
| `student-profile.html` | student | Goals, skills, expected mentor expertise, format, duration, availability |
| `student-mentor.html` | student | Status and next step, assigned mentor, readiness, feedback, concerns |
| `mentor.html` | mentor | Accept or decline match requests, mentees |
| `mentor-profile.html` | mentor | Background and availability slots |
| `admin.html` | coordinator | Profile counts, matches by status, delayed proposals, concerns, feedback |
| `admin-students.html` | coordinator | View, search and filter student profiles and readiness |
| `admin-mentors.html` | coordinator | Review, edit and verify mentor profiles and availability |
| `admin-matches.html` | coordinator | Compare student and mentor, propose matches, change match status |

Shared files: `styles.css`, `app.js` (sample data, navigation, helpers).

## Workflow shown
The coordinator proposes a match, the mentor accepts or declines, and only then does the student see the mentor. Statuses: proposed, active (the mentor accepted), completed, cancelled. Students and mentors never browse each other.

## Limitations
Sample data is stored in the browser (localStorage) so the flow can be tried. There is no backend, real authentication or email. Passwords are stored in plain text for the demo only. Use "Reset demo data" on the login page to start over.
