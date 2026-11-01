# Team 032 – Milestone 2 Frontend Prototype

Student Mentoring and Career Support Platform. Plain HTML, CSS and JavaScript. No install or build step.

## Run
1. Unzip the package and open the `frontend` folder.
2. Open `index.html` in Chrome, Edge or Firefox (double-click is enough).
3. Log in with a demo account (password `demo123`):
   - Student: `asha@student.test`
   - Mentor: `meera@mentor.test`
   - Admin: `admin@client.test`

## Pages
| Page | Role | Purpose |
|---|---|---|
| `index.html`, `register.html` | all | Log in, create an account |
| `student.html` | student | Dashboard, match status, notifications |
| `student-profile.html` | student | Goals, skills, wanted topics, format, duration, availability |
| `student-mentor.html` | student | Status and next step, proposed mentor to accept or decline, feedback, concerns |
| `mentor.html` | mentor | Accept or decline match requests, active mentees |
| `mentor-profile.html` | mentor | Background, topics, maximum students, availability slots |
| `admin.html` | admin | Action cards, recommended matches, mentor capacity, pipeline, concerns, feedback |
| `admin-students.html` | admin | View, search and filter student profiles and responses |
| `admin-mentors.html` | admin | Review, edit and verify mentor profiles and availability |
| `admin-matches.html` | admin | Recommended matches with scores, compare student and mentor, propose, confirm or cancel, change status |

Shared files: `styles.css`, `app.js` (sample data, navigation, helpers).

## Workflow shown
The admin proposes a match and both the mentor and the student are notified. Each accepts or declines. Only when both have accepted can the admin confirm the match, which makes it active; the admin can cancel it instead. Statuses: proposed, active (confirmed by the admin), completed, cancelled. Students and mentors never browse each other.

## Matching
The platform gives every waiting student and every verified mentor with free places a score out of 100: topic overlap 70 and mentor experience 30. It lists the best mentors with reasons. It only recommends: the admin proposes, both sides accept, and the admin confirms. Each mentor sets a maximum number of students; a proposal over that limit is refused.

## Limitations
Sample data is stored in the browser (localStorage) so the flow can be tried. There is no backend, real authentication or email. Passwords are stored in plain text for the demo only. Use "Reset demo data" on the login page to start over.
