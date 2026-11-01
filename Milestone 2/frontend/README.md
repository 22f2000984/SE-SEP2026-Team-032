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
| `student-profile.html` | student | Goals, skills, wanted topics, format, duration, free times |
| `student-mentor.html` | student | Status and next step, proposed mentor to accept or decline, feedback, concerns |
| `mentor.html` | mentor | Accept or decline match requests, active mentees |
| `mentor-profile.html` | mentor | Background, topics, maximum students, availability slots |
| `admin.html` | coordinator | Action cards, recommended matches, mentor capacity, pipeline, concerns, feedback |
| `admin-students.html` | coordinator | View, search and filter student profiles and responses |
| `admin-mentors.html` | coordinator | Review, edit and verify mentor profiles and availability |
| `admin-matches.html` | coordinator | Recommended matches with scores, compare student and mentor, propose, confirm or cancel, change status |

Shared files: `styles.css`, `app.js` (sample data, navigation, helpers).

## Workflow shown
The coordinator proposes a match and both the mentor and the student are notified. Each accepts or declines. Only when both have accepted can the coordinator confirm the match, which makes it active; the coordinator can cancel it instead. Statuses: proposed, active (confirmed by the coordinator), completed, cancelled. Students and mentors never browse each other.

## Matching
The platform scores every waiting student against every verified mentor with free places (out of 100: topics 40, time overlap 30, free places 15, experience 15) and lists the best mentors with reasons. It only recommends: the coordinator proposes, both sides accept, and the coordinator confirms. Each mentor sets a maximum number of students; a proposal over that limit is refused.

## Limitations
Sample data is stored in the browser (localStorage) so the flow can be tried. There is no backend, real authentication or email. Passwords are stored in plain text for the demo only. Use "Reset demo data" on the login page to start over.
