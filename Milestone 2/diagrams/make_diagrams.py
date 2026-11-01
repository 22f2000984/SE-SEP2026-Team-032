"""Generates the Milestone 2 ER and class diagrams as SVG.

Usage: python3 make_diagrams.py   (writes er_diagram.svg and class_diagram.svg here)
Convert to PNG with headless Chrome, see README.md in this folder.
"""
import os
from xml.sax.saxutils import escape

OUT = os.path.dirname(os.path.abspath(__file__))
NAVY, BLUE, LIGHT, TEXT = "#12345a", "#1769aa", "#f4f7fb", "#243447"
LH = 20  # line height


class Diagram:
    def __init__(self, w, h, title):
        self.w, self.h, self.parts = w, h, []
        self.parts.append(f'<text x="40" y="42" font-size="26" font-weight="700" fill="{NAVY}">{escape(title)}</text>')

    def box(self, x, y, w, title, sections, stereo=None, head=NAVY):
        hh = 34 + (16 if stereo else 0)
        body = sum(len(s) for s in sections) * LH + 14 * len(sections) + 4
        h = hh + body
        p = self.parts
        p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{LIGHT}" stroke="{BLUE}" stroke-width="2"/>')
        p.append(f'<path d="M{x},{y+hh} V{y+6} Q{x},{y} {x+6},{y} H{x+w-6} Q{x+w},{y} {x+w},{y+6} V{y+hh} Z" fill="{head}"/>')
        ty = y + 23
        if stereo:
            p.append(f'<text x="{x+w/2}" y="{y+17}" text-anchor="middle" font-size="12" fill="#cfe3f5" font-style="italic">{escape(stereo)}</text>')
            ty += 16
        p.append(f'<text x="{x+w/2}" y="{ty}" text-anchor="middle" font-size="16" font-weight="700" fill="#fff">{escape(title)}</text>')
        cy = y + hh + 6
        for i, sec in enumerate(sections):
            if i:
                p.append(f'<line x1="{x}" y1="{cy-2}" x2="{x+w}" y2="{cy-2}" stroke="{BLUE}"/>')
                cy += 6
            for line in sec:
                weight = "700" if line.startswith(("PK ", "FK ")) else "400"
                p.append(f'<text x="{x+12}" y="{cy+14}" font-size="13" font-weight="{weight}" fill="{TEXT}">{escape(line)}</text>')
                cy += LH
            cy += 8
        return dict(x=x, y=y, w=w, h=h, cx=x + w / 2, bottom=y + h, right=x + w)

    def line(self, pts, start=None, end=None, dashed=False, arrow=None, hollow=False):
        d = " ".join(f"{a},{b}" for a, b in pts)
        extra = ' stroke-dasharray="6 4"' if dashed else ""
        m = ""
        if hollow:
            m = ' marker-end="url(#tri)"'
        elif arrow:
            m = ' marker-end="url(#arr)"'
        self.parts.append(f'<polyline points="{d}" fill="none" stroke="{TEXT}" stroke-width="1.6"{extra}{m}/>')
        if start:
            self.label(pts[0], pts[1], start)
        if end:
            self.label(pts[-1], pts[-2], end)

    def label(self, at, toward, txt):
        (x, y), (x2, y2) = at, toward
        dx = 0 if x2 == x else (16 if x2 > x else -16)
        dy = 0 if y2 == y else (18 if y2 > y else -18)
        lx, ly = x + dx, y + dy
        if dx == 0:
            lx += 12
        if dy == 0:
            ly -= 8
        self.parts.append(f'<text x="{lx}" y="{ly}" text-anchor="middle" font-size="13" font-weight="700" fill="{BLUE}">{escape(txt)}</text>')

    def text(self, x, y, txt, size=12, anchor="middle", color=TEXT):
        self.parts.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{color}" font-style="italic">{escape(txt)}</text>')

    def save(self, name):
        defs = (f'<defs><marker id="tri" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="14" markerHeight="14" orient="auto">'
                f'<path d="M1,1 L11,6 L1,11 Z" fill="#fff" stroke="{TEXT}" stroke-width="1.4"/></marker>'
                f'<marker id="arr" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="10" markerHeight="10" orient="auto">'
                f'<path d="M1,1 L11,6 L1,11" fill="none" stroke="{TEXT}" stroke-width="1.6"/></marker></defs>')
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}" '
               f'font-family="Arial, Helvetica, sans-serif"><rect width="100%" height="100%" fill="#fff"/>{defs}' + "".join(self.parts) + "</svg>")
        with open(os.path.join(OUT, name), "w") as f:
            f.write(svg)


def er():
    d = Diagram(2300, 1480, "Entity Relationship Diagram: Student Mentoring Platform (client-mediated)")
    W = 360
    c = [40, 500, 960, 1420, 1880]
    sa = d.box(c[0], 80, W, "STUDENT_AVAILABILITY_SLOT", [["PK slot_id", "FK student_id", "day_of_week", "time_band (morning | afternoon |", "           evening)"]])
    student = d.box(c[1], 80, W, "STUDENT_PROFILE", [
        ["PK student_id", "FK user_id  (UNIQUE)", "programme_level", "career_goals", "skills", "mentoring_format",
         "expected_duration", "preferences", "availability_note", "updated_at"]])
    user = d.box(c[2], 80, W, "USER", [
        ["PK user_id", "email  (UNIQUE)", "password_hash", "full_name", "role (student | mentor | admin)", "is_active", "created_at"]])
    mentor = d.box(c[3], 80, W, "MENTOR_PROFILE", [
        ["PK mentor_id", "FK user_id  (UNIQUE)", "qualifications", "experience_years", "bio",
         "profile_status (pending | verified)", "max_students  (1 to 10)", "updated_at"]])
    slot = d.box(c[4], 80, W, "AVAILABILITY_SLOT", [
        ["PK slot_id", "FK mentor_id", "day_of_week", "start_time", "end_time", "timezone", "is_active"]])
    ys = 80 + 120
    d.line([(sa["right"], ys), (student["x"], ys)], "N", "1")
    d.line([(student["right"], ys), (user["x"], ys)], "1", "1")
    d.line([(user["right"], ys), (mentor["x"], ys)], "1", "1")
    d.line([(mentor["right"], ys), (slot["x"], ys)], "1", "N")
    # shared topic list: STUDENT_TOPIC - EXPERTISE_TOPIC - MENTOR_TOPIC
    ty = 470
    st = d.box(620, ty, 240, "STUDENT_TOPIC", [["FK student_id", "FK topic_id"]])
    tp = d.box(1020, ty, 240, "EXPERTISE_TOPIC", [["PK topic_id", "name  (UNIQUE)"]])
    mt = d.box(1420, ty, 240, "MENTOR_TOPIC", [["FK mentor_id", "FK topic_id"]])
    d.line([(student["x"] + 240, student["bottom"]), (st["cx"], st["y"])], "1", "N")
    d.line([(mentor["x"] + 120, mentor["bottom"]), (mt["cx"], mt["y"])], "1", "N")
    my = ty + 50
    d.line([(st["right"], my), (tp["x"], my)], "N", "1")
    d.line([(mt["x"], my), (tp["right"], my)], "N", "1")
    match = d.box(c[2], 750, W, "MATCH", [
        ["PK match_id", "FK student_id", "FK mentor_id", "FK proposed_by  (admin USER)",
         "status (proposed | active |", "           completed | cancelled)", "mentor_response (pending |", "           accepted | declined)", "mentor_responded_at",
         "student_response (pending |", "           accepted | declined)", "student_responded_at", "match_score  (0 to 100)", "score_reasons", "notes", "proposed_at", "confirmed_at"]])
    d.line([(user["x"] + 330, user["bottom"]), (user["x"] + 330, match["y"])], "1", "N")
    d.text(user["x"] + 345, 640, "proposes", anchor="start")
    ym = match["y"] + 130
    d.line([(student["x"] + 40, student["bottom"]), (student["x"] + 40, ym), (match["x"], ym)], "1", "N")
    d.line([(mentor["x"] + 300, mentor["bottom"]), (mentor["x"] + 300, ym), (match["right"], ym)], "1", "N")
    d.text(student["x"] + 56, ym - 10, "is matched in", anchor="start")
    d.text(mentor["x"] + 284, ym - 10, "is matched in", anchor="end")
    row3 = 1220
    boxes = [
        ("MATCH_STATUS_LOG", ["PK log_id", "FK match_id", "old_status", "new_status", "FK changed_by  (USER)", "changed_at"]),
        ("FEEDBACK", ["PK feedback_id", "FK match_id", "FK author_id  (USER)", "rating (1 to 5)", "comments", "created_at"]),
        ("CONCERN", ["PK concern_id", "FK match_id", "FK raised_by  (USER)", "description", "status (open | resolved)", "created_at"]),
        ("NOTIFICATION", ["PK notification_id", "FK user_id", "FK match_id  (NULL allowed)", "message", "is_read", "sent_at"]),
    ]
    busy = row3 - 40
    for i, (n, f) in enumerate(boxes):
        b = d.box(40 + i * 460, row3, W, n, [f])
        d.line([(match["cx"], match["bottom"]), (match["cx"], busy), (b["cx"], busy), (b["cx"], b["y"])], "1" if i == 1 else None, "N")
    d.text(1150, 1460, "PK = primary key, FK = foreign key. 1 / N shows how many rows on each side of a relationship. Match scores are calculated on request; only the score at proposal time is stored.", size=13)
    d.save("er_diagram.svg")


def cls():
    d = Diagram(1960, 1860, "Class Diagram: Student Mentoring Platform (client-mediated)")
    user = d.box(700, 80, 400, "User", [
        ["- userId: int", "- email: string", "- passwordHash: string", "- fullName: string", "- role: Role"],
        ["+ login(): Token", "+ logout()", "+ updateAccount()"]], stereo="<<abstract>>")
    student = d.box(40, 380, 420, "Student", [
        ["- programmeLevel: string", "- careerGoals: string", "- skills: string[]", "- expectedTopics: Topic[]",
         "- mentoringFormat: Format", "- expectedDuration: string", "- preferences: string",
         "- availabilityNote: string"],
        ["+ updateProfile()", "+ setAvailability(slots)", "+ viewAssignedMentor(): Match", "+ acceptMatch(m: Match)", "+ declineMatch(m: Match)", "+ submitFeedback()", "+ raiseConcern()"]])
    mentor = d.box(680, 380, 440, "Mentor", [
        ["- qualifications: string", "- experienceYears: int", "- topics: Topic[]", "- bio: string", "- profileStatus: ProfileStatus", "- maxStudents: int"],
        ["+ updateProfile()", "+ setAvailability(slots)", "+ setCapacity(n: int)", "+ freePlaces(): int", "+ acceptMatch(m: Match)", "+ declineMatch(m: Match)"]])
    sslot = d.box(40, 130, 420, "StudentSlot", [["- slotId: int", "- dayOfWeek: string", "- timeBand: TimeBand"]])
    slot = d.box(1200, 380, 300, "AvailabilitySlot", [
        ["- slotId: int", "- dayOfWeek: string", "- startTime: time", "- endTime: time", "- isActive: bool"]])
    admin = d.box(1560, 380, 360, "Administrator", [
        ["- adminId: int"],
        ["+ viewStudentProfiles()", "+ editMentorProfile()", "+ verifyMentorProfile()", "+ viewRecommendations()", "+ proposeMatch(s, m): Match", "+ confirmMatch(m: Match)", "+ changeStatus(m, status)", "+ viewOverview()", "+ viewFeedback()", "+ resolveConcern()"]])
    match = d.box(680, 800, 440, "Match", [
        ["- matchId: int", "- status: MatchStatus", "- notes: string", "- proposedAt: datetime", "- matchScore: int", "- scoreReasons: string", "- mentorResponse: Response", "- studentResponse: Response",
         "- mentorRespondedAt: datetime", "- studentRespondedAt: datetime", "- confirmedAt: datetime"],
        ["+ recordResponse(by, answer)", "+ bothAccepted(): bool", "+ confirm()  [only if both accepted]", "+ complete()", "+ cancel()"]])
    # inheritance (hollow triangle at User)
    bus = user["bottom"] + 30
    for b in (student, mentor, admin):
        pts = [(b["cx"], b["y"]), (b["cx"], bus), (user["cx"], bus), (user["cx"], user["bottom"])] if b["cx"] != user["cx"] else \
              [(b["cx"], b["y"]), (user["cx"], user["bottom"])]
        d.line(pts, hollow=True)
    d.line([(mentor["right"], 520), (slot["x"], 520)], "1", "0..*")
    d.line([(120, sslot["bottom"]), (120, student["y"])], "0..*", "1")
    # associations to Match
    ym = match["y"] + 90
    d.line([(student["cx"], student["bottom"]), (student["cx"], ym), (match["x"], ym)], "1", "0..*")
    d.line([(mentor["cx"], mentor["bottom"]), (match["cx"], match["y"])], "1", "0..*")
    d.line([(admin["cx"], admin["bottom"]), (admin["cx"], ym), (match["right"], ym)], "1", "0..*")
    d.text(student["cx"] + 16, ym - 10, "is matched in", anchor="start")
    d.text(admin["cx"] - 16, ym - 10, "proposes", anchor="end")
    # row 4
    row4 = 1300
    busy = row4 - 40
    W4, STEP = 290, 320
    fb = d.box(40, row4, W4, "Feedback", [["- feedbackId: int", "- rating: int", "- comments: string", "- createdAt: datetime"]])
    co = d.box(40 + STEP, row4, W4, "Concern", [["- concernId: int", "- description: string", "- status: ConcernStatus", "- createdAt: datetime"]])
    no = d.box(40 + 2 * STEP, row4, W4, "Notification", [["- notificationId: int", "- message: string", "- isRead: bool", "- sentAt: datetime"]])
    lg = d.box(40 + 3 * STEP, row4, W4, "MatchStatusLog", [["- logId: int", "- oldStatus: MatchStatus", "- newStatus: MatchStatus", "- changedAt: datetime"]])
    en = d.box(40 + 4 * STEP, row4, W4, "MatchStatus", [["proposed", "active", "completed", "cancelled"]], stereo="<<enumeration>>", head=BLUE)
    rs = d.box(40 + 5 * STEP, row4, W4, "Response", [["pending", "accepted", "declined"]], stereo="<<enumeration>>", head=BLUE)
    for b, m in ((fb, "0..*"), (co, "0..*"), (no, "0..*"), (lg, "0..*")):
        d.line([(match["cx"], match["bottom"]), (match["cx"], busy), (b["cx"], busy), (b["cx"], b["y"])], None, m)
    d.line([(match["right"], match["y"] + 240), (en["cx"], match["y"] + 240), (en["cx"], en["y"])], dashed=True, arrow=True)
    d.text(en["cx"] - 10, match["y"] + 228, "uses", anchor="end")
    d.line([(match["right"], match["y"] + 270), (rs["cx"], match["y"] + 270), (rs["cx"], rs["y"])], dashed=True, arrow=True)
    d.text(rs["cx"] - 10, match["y"] + 258, "uses", anchor="end")
    row5 = 1520
    ms = d.box(40, row5, 420, "MatchingService", [["- expertiseWeight: int = 40", "- availabilityWeight: int = 30", "- capacityWeight: int = 15", "- experienceWeight: int = 15", "- minGoodScore: int = 40"],
        ["+ isEligible(s: Student, m: Mentor): bool", "+ score(s: Student, m: Mentor): MatchScore", "+ recommend(s: Student, n: int): MatchScore[]"]], stereo="<<service>>")
    sc = d.box(540, row5, 340, "MatchScore", [["- total: int", "- expertisePoints: int", "- availabilityPoints: int", "- capacityPoints: int", "- experiencePoints: int", "- reasons: string[]"]])
    d.line([(ms["right"], row5 + 110), (sc["x"], row5 + 110)], dashed=True, arrow=True)
    d.text((ms["right"] + sc["x"]) / 2, row5 + 98, "creates", size=12)
    d.box(960, row5, 300, "Topic", [["Data Science", "Web Development", "Career Switching", "Interview Preparation", "Product Management", "Higher Studies", "Entrepreneurship", "Cloud and DevOps"]], stereo="<<enumeration>>", head=BLUE)
    d.box(1300, row5, 260, "TimeBand", [["morning", "afternoon", "evening"]], stereo="<<enumeration>>", head=BLUE)
    d.box(1600, row5, 300, "Format", [["No preference", "Video call", "Phone call", "Messaging"]], stereo="<<enumeration>>", head=BLUE)
    d.text(980, 1830, "Students and mentors never browse each other. The Administrator asks the MatchingService for scored recommendations, then proposes, confirms or cancels each Match.", size=13)
    d.save("class_diagram.svg")


if __name__ == "__main__":
    er()
    cls()
