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
    d = Diagram(1840, 1190, "Entity Relationship Diagram: Student Mentoring Platform (client-mediated)")
    W = 360
    student = d.box(40, 80, W, "STUDENT_PROFILE", [
        ["PK student_id", "FK user_id  (UNIQUE)", "programme_level", "career_goals", "skills", "expected_mentor_expertise",
         "mentoring_format", "expected_duration", "preferences", "availability_note", "updated_at"]])
    user = d.box(500, 80, W, "USER", [
        ["PK user_id", "email  (UNIQUE)", "password_hash", "full_name",
         "role (student | mentor | admin)", "is_active", "created_at"]])
    mentor = d.box(960, 80, W, "MENTOR_PROFILE", [
        ["PK mentor_id", "FK user_id  (UNIQUE)", "qualifications", "experience_years", "expertise_areas", "bio",
         "profile_status (pending | verified)", "updated_at"]])
    slot = d.box(1420, 80, W, "AVAILABILITY_SLOT", [
        ["PK slot_id", "FK mentor_id", "day_of_week", "start_time", "end_time", "timezone", "is_active"]])
    match = d.box(500, 470, W, "MATCH", [
        ["PK match_id", "FK student_id", "FK mentor_id", "FK proposed_by  (admin USER)",
         "status (proposed | active |", "           completed | cancelled)", "mentor_response (pending |", "           accepted | declined)", "mentor_responded_at",
         "student_response (pending |", "           accepted | declined)", "student_responded_at", "notes", "proposed_at", "confirmed_at"]])
    ys = 80 + 120
    d.line([(student["right"], ys), (user["x"], ys)], "1", "1")
    d.line([(user["right"], ys), (mentor["x"], ys)], "1", "1")
    d.line([(mentor["right"], ys), (slot["x"], ys)], "1", "N")
    d.line([(user["cx"], user["bottom"]), (match["cx"], match["y"])], "1", "N")
    d.text(user["cx"] + 70, (user["bottom"] + match["y"]) / 2, "proposes", anchor="start")
    ym = match["y"] + 130
    d.line([(student["cx"], student["bottom"]), (student["cx"], ym), (match["x"], ym)], "1", "N")
    d.line([(mentor["cx"], mentor["bottom"]), (mentor["cx"], ym), (match["right"], ym)], "1", "N")
    d.text(student["cx"] + 16, ym - 10, "is matched in", anchor="start")
    d.text(mentor["cx"] - 16, ym - 10, "is matched in", anchor="end")
    row3 = 900
    boxes = [
        ("MATCH_STATUS_LOG", ["PK log_id", "FK match_id", "old_status", "new_status", "FK changed_by  (USER)", "changed_at"]),
        ("FEEDBACK", ["PK feedback_id", "FK match_id", "FK author_id  (USER)", "rating (1 to 5)", "comments", "created_at"]),
        ("CONCERN", ["PK concern_id", "FK match_id", "FK raised_by  (USER)", "description", "status (open | resolved)", "created_at"]),
        ("NOTIFICATION", ["PK notification_id", "FK user_id", "FK match_id  (NULL allowed)", "message", "is_read", "sent_at"]),
    ]
    busy = row3 - 40
    for i, (n, f) in enumerate(boxes):
        b = d.box(40 + i * 460, row3, W, n, [f])
        d.line([(match["cx"], match["bottom"]), (match["cx"], busy), (b["cx"], busy), (b["cx"], b["y"])] if i != 1 else
               [(match["cx"], match["bottom"]), (b["cx"], b["y"])] if b["cx"] == match["cx"] else
               [(match["cx"], match["bottom"]), (match["cx"], busy), (b["cx"], busy), (b["cx"], b["y"])],
               "1" if i == 1 else None, "N")
    d.text(920, 1160, "PK = primary key, FK = foreign key. 1 / N shows how many rows on each side of a relationship.", size=13)
    d.save("er_diagram.svg")


def cls():
    d = Diagram(1960, 1560, "Class Diagram: Student Mentoring Platform (client-mediated)")
    user = d.box(700, 80, 400, "User", [
        ["- userId: int", "- email: string", "- passwordHash: string", "- fullName: string", "- role: Role"],
        ["+ login(): Token", "+ logout()", "+ updateAccount()"]], stereo="<<abstract>>")
    student = d.box(40, 380, 420, "Student", [
        ["- programmeLevel: string", "- careerGoals: string", "- skills: string[]", "- expectedMentorExpertise: string",
         "- mentoringFormat: Format", "- expectedDuration: string", "- preferences: string",
         "- availabilityNote: string"],
        ["+ updateProfile()", "+ viewAssignedMentor(): Match", "+ acceptMatch(m: Match)", "+ declineMatch(m: Match)", "+ submitFeedback()", "+ raiseConcern()"]])
    mentor = d.box(680, 380, 440, "Mentor", [
        ["- qualifications: string", "- experienceYears: int", "- expertiseAreas: string[]", "- bio: string", "- profileStatus: ProfileStatus"],
        ["+ updateProfile()", "+ setAvailability(slots)", "+ acceptMatch(m: Match)", "+ declineMatch(m: Match)"]])
    slot = d.box(1200, 380, 300, "AvailabilitySlot", [
        ["- slotId: int", "- dayOfWeek: string", "- startTime: time", "- endTime: time", "- isActive: bool"]])
    admin = d.box(1560, 380, 360, "Administrator", [
        ["- adminId: int"],
        ["+ viewStudentProfiles()", "+ editMentorProfile()", "+ verifyMentorProfile()", "+ proposeMatch(s, m): Match", "+ confirmMatch(m: Match)", "+ changeStatus(m, status)", "+ viewOverview()", "+ viewFeedback()", "+ resolveConcern()"]])
    match = d.box(680, 800, 440, "Match", [
        ["- matchId: int", "- status: MatchStatus", "- notes: string", "- proposedAt: datetime", "- mentorResponse: Response", "- studentResponse: Response",
         "- mentorRespondedAt: datetime", "- studentRespondedAt: datetime", "- confirmedAt: datetime"],
        ["+ recordResponse(by, answer)", "+ bothAccepted(): bool", "+ confirm()  [only if both accepted]", "+ complete()", "+ cancel()"]])
    # inheritance (hollow triangle at User)
    bus = user["bottom"] + 30
    for b in (student, mentor, admin):
        pts = [(b["cx"], b["y"]), (b["cx"], bus), (user["cx"], bus), (user["cx"], user["bottom"])] if b["cx"] != user["cx"] else \
              [(b["cx"], b["y"]), (user["cx"], user["bottom"])]
        d.line(pts, hollow=True)
    d.line([(mentor["right"], 520), (slot["x"], 520)], "1", "0..*")
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
    d.text(980, 1530, "Students and mentors never browse each other: every Match is proposed by an Administrator, who tracks its status.", size=13)
    d.save("class_diagram.svg")


if __name__ == "__main__":
    er()
    cls()
