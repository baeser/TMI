#!/usr/bin/env python3
"""Generate the TMI Student Investigation Worksheet PDF."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import black, HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether, Flowable
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

# ── Colors ──
DARK_BLUE = HexColor("#1a2a4a")
ACCENT = HexColor("#c47a00")
GRAY = HexColor("#666666")
LIGHT_GRAY = HexColor("#cccccc")
RULE_GRAY = HexColor("#b0b0b0")


# ── Custom flowable: ruled lines for handwriting ──
class RuledLines(Flowable):
    """Draw horizontal ruled lines for student handwriting."""
    def __init__(self, width, num_lines, line_spacing=22):
        super().__init__()
        self.width = width
        self.num_lines = num_lines
        self.line_spacing = line_spacing
        self._fixedWidth = width
        self._fixedHeight = num_lines * line_spacing

    def wrap(self, availWidth, availHeight):
        return self.width, self._fixedHeight

    def draw(self):
        self.canv.setStrokeColor(RULE_GRAY)
        self.canv.setLineWidth(0.4)
        for i in range(self.num_lines):
            y = self._fixedHeight - (i + 1) * self.line_spacing
            self.canv.line(0, y, self.width, y)


class ThinHR(Flowable):
    """A thin horizontal rule divider."""
    def __init__(self, width, color=LIGHT_GRAY, thickness=0.75):
        super().__init__()
        self.width = width
        self.color = color
        self.thickness = thickness
        self._fixedWidth = width
        self._fixedHeight = 6

    def wrap(self, availWidth, availHeight):
        return self.width, self._fixedHeight

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 3, self.width, 3)


# ── Page dimensions ──
PAGE_W, PAGE_H = letter
MARGIN = 0.75 * inch
CONTENT_W = PAGE_W - 2 * MARGIN


# ── Styles ──
style_title = ParagraphStyle(
    "Title", fontName="Helvetica-Bold", fontSize=18,
    leading=22, textColor=DARK_BLUE, alignment=TA_CENTER,
    spaceAfter=2,
)
style_subtitle = ParagraphStyle(
    "Subtitle", fontName="Helvetica-Oblique", fontSize=10,
    leading=14, textColor=GRAY, alignment=TA_CENTER,
    spaceAfter=4,
)
style_section = ParagraphStyle(
    "Section", fontName="Helvetica-Bold", fontSize=13,
    leading=17, textColor=DARK_BLUE, spaceBefore=10, spaceAfter=2,
)
style_scene_meta = ParagraphStyle(
    "SceneMeta", fontName="Helvetica-Oblique", fontSize=8.5,
    leading=11, textColor=GRAY, spaceAfter=6,
)
style_question = ParagraphStyle(
    "Question", fontName="Helvetica-Bold", fontSize=9.5,
    leading=13, textColor=black, spaceBefore=4, spaceAfter=2,
)
style_question_italic = ParagraphStyle(
    "QuestionItalic", fontName="Helvetica-BoldOblique", fontSize=9.5,
    leading=13, textColor=ACCENT, spaceBefore=4, spaceAfter=2,
)
style_instructions = ParagraphStyle(
    "Instructions", fontName="Helvetica", fontSize=8.5,
    leading=12, textColor=GRAY, spaceAfter=0,
)
style_footer = ParagraphStyle(
    "Footer", fontName="Helvetica", fontSize=7.5,
    leading=10, textColor=GRAY, alignment=TA_CENTER,
)


# ── Header/footer callback ──
def page_header_footer(canvas_obj, doc):
    canvas_obj.saveState()
    # Footer line
    canvas_obj.setStrokeColor(LIGHT_GRAY)
    canvas_obj.setLineWidth(0.5)
    canvas_obj.line(MARGIN, 0.55 * inch, PAGE_W - MARGIN, 0.55 * inch)
    # Footer text
    canvas_obj.setFont("Helvetica", 7.5)
    canvas_obj.setFillColor(GRAY)
    canvas_obj.drawString(MARGIN, 0.38 * inch,
                          "TMI: March 1979 \u2014 Student Investigation Worksheet")
    canvas_obj.drawRightString(PAGE_W - MARGIN, 0.38 * inch,
                               f"Page {doc.page}")
    canvas_obj.restoreState()


# ── Helper to build a question + ruled lines ──
def q(text, lines=3, choice=False):
    """Return a list of flowables for one question with answer lines."""
    st = style_question_italic if choice else style_question
    return KeepTogether([
        Paragraph(text, st),
        Spacer(1, 3),
        RuledLines(CONTENT_W, lines),
        Spacer(1, 6),
    ])


# ── Build the document ──
def build_pdf(path):
    doc = SimpleDocTemplate(
        path, pagesize=letter,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=0.8 * inch,
    )

    story = []

    # ── COVER / HEADER ──
    story.append(Spacer(1, 8))
    story.append(Paragraph("Three Mile Island: March 1979", style_title))
    story.append(Paragraph("Student Investigation Worksheet", ParagraphStyle(
        "Title2", fontName="Helvetica", fontSize=12, leading=16,
        textColor=ACCENT, alignment=TA_CENTER, spaceAfter=4,
    )))
    story.append(Spacer(1, 2))
    story.append(ThinHR(CONTENT_W, color=DARK_BLUE, thickness=1.5))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Complete this worksheet as you progress through the simulation. "
        "Answer each question in the space provided. For choice questions, "
        "record which option you selected and explain your reasoning.",
        style_instructions,
    ))
    story.append(Spacer(1, 12))

    # Name / Date / Period row
    name_table = Table(
        [["Name: _________________________________",
          "Date: ________________",
          "Period: ______"]],
        colWidths=[3.4 * inch, 2.0 * inch, 1.2 * inch],
    )
    name_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (-1, -1), black),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
    ]))
    story.append(name_table)
    story.append(Spacer(1, 10))
    story.append(ThinHR(CONTENT_W))
    story.append(Spacer(1, 6))

    # ════════════════════════════════════════════
    # SECTION 1
    # ════════════════════════════════════════════
    story.append(Paragraph("Scene 1: The Call", style_section))
    story.append(Paragraph(
        "NRC Region I Office, King of Prussia, PA \u2014 March 28, 1979, 7:15 a.m.",
        style_scene_meta))
    story.append(q(
        "1. What is the NRC, and what is your role in this simulation?", 3))
    story.append(q(
        "2. What has happened at Three Mile Island? Summarize the initial report "
        "from your supervisor.", 4))
    story.append(q(
        "YOUR CHOICE: Which option did you choose (A or B)? Why?", 3, choice=True))

    story.append(ThinHR(CONTENT_W))

    # ════════════════════════════════════════════
    # SECTION 2
    # ════════════════════════════════════════════
    story.append(Paragraph("Scene 2: The Island", style_section))
    story.append(Paragraph(
        "Three Mile Island, Dauphin County, PA \u2014 March 28, 1979, 9:30 a.m.",
        style_scene_meta))
    story.append(q(
        "3. What is your first visual clue that something is wrong when you "
        "arrive at TMI?", 3))
    story.append(q(
        "4. The Met Ed site manager says the situation is \u201cstabilized.\u201d "
        "A fellow NRC inspector disagrees. What does the inspector tell you, "
        "and why is this important?", 4))

    story.append(ThinHR(CONTENT_W))

    # ════════════════════════════════════════════
    # SECTION 3
    # ════════════════════════════════════════════
    story.append(Paragraph("Scene 3: The Control Room", style_section))
    story.append(Paragraph(
        "TMI Unit 2 Control Room \u2014 March 28, 1979, 10:00 a.m.",
        style_scene_meta))
    story.append(q(
        "5. Describe the sequence of events that caused the accident. Use the "
        "following terms in your answer: feedwater pumps, SCRAM, decay heat, "
        "PORV, loss of coolant accident (LOCA).", 6))

    story.append(PageBreak())

    story.append(Paragraph("Scene 3: The Control Room (continued)", style_section))
    story.append(Spacer(1, 4))
    story.append(q(
        "6. What was the critical design flaw in the control room "
        "instrumentation? Why did it matter?", 4))
    story.append(q(
        "7. The operators reduced emergency cooling water flow. Why did they "
        "make this decision, and why was it wrong?", 4))
    story.append(q(
        "8. HISTORICAL CONNECTION: The Davis-Besse plant in Ohio had a nearly "
        "identical incident in 1977. Why didn\u2019t the lessons from Davis-Besse "
        "prevent the TMI accident?", 4))
    story.append(q(
        "YOUR CHOICE: Did you focus on reactor status (A) or radiation "
        "releases (B)? What did you learn from that path?", 3, choice=True))
    story.append(q(
        "INCIDENT REPORT: After you fill out the in-simulation incident report, "
        "summarize what you wrote for Core Status and Recommendations below.", 4,
        choice=True))

    story.append(ThinHR(CONTENT_W))

    # ════════════════════════════════════════════
    # SECTION 4
    # ════════════════════════════════════════════
    story.append(Paragraph("Scene 4: Conflicting Signals", style_section))
    story.append(Paragraph(
        "Three Mile Island / Middletown, PA \u2014 March 28\u201329, 1979",
        style_scene_meta))
    story.append(q(
        "9. How did Met Ed describe the situation to the press? How did this "
        "compare to what you knew as an NRC inspector on the ground?", 4))
    story.append(q(
        "10. Lt. Governor Scranton initially told the public there was "
        "\u201cno danger,\u201d then reversed his statement. Why is this "
        "reversal significant?", 4))

    story.append(PageBreak())

    story.append(Paragraph("Scene 4: Conflicting Signals (continued)", style_section))
    story.append(Spacer(1, 4))
    story.append(q(
        "11. What is the hydrogen bubble, and why was it so terrifying?", 4))
    story.append(q(
        "YOUR CHOICE: Did you recommend evacuation (A) or sheltering in "
        "place (B)? Explain your reasoning.", 4, choice=True))

    story.append(ThinHR(CONTENT_W))

    # ════════════════════════════════════════════
    # SECTION 5
    # ════════════════════════════════════════════
    story.append(Paragraph("Scene 5: The Hydrogen Bubble", style_section))
    story.append(Paragraph(
        "Three Mile Island / Governor\u2019s Office, Harrisburg \u2014 "
        "March 30, 1979", style_scene_meta))
    story.append(q(
        "12. NRC Chairman Hendrie said he and the governor were \u201clike a "
        "couple of blind men staggering around making decisions.\u201d What "
        "does this reveal about the crisis?", 4))
    story.append(q(
        "13. How many people voluntarily evacuated the TMI area? What does "
        "this tell you about public trust in the institutions managing "
        "the crisis?", 4))
    story.append(q(
        "YOUR CHOICE: Did you focus on the technical problem (A) or public "
        "communication (B)? What was the outcome of your choice?", 3, choice=True))

    story.append(ThinHR(CONTENT_W))

    # ════════════════════════════════════════════
    # SECTION 6
    # ════════════════════════════════════════════
    story.append(Paragraph("Scene 6: The President Arrives", style_section))
    story.append(Paragraph(
        "Three Mile Island, PA \u2014 April 1, 1979", style_scene_meta))
    story.append(q(
        "14. Why was President Carter uniquely qualified to visit TMI? "
        "What was his relevant background?", 3))

    story.append(PageBreak())

    story.append(Paragraph("Scene 6: The President Arrives (continued)", style_section))
    story.append(Spacer(1, 4))
    story.append(q(
        "15. What did the 1985 remote camera inspection reveal about the "
        "reactor core? How did the actual damage compare to what officials "
        "said during the crisis?", 5))

    story.append(ThinHR(CONTENT_W))

    # ════════════════════════════════════════════
    # SECTION 7
    # ════════════════════════════════════════════
    story.append(Paragraph("Scene 7: The Investigation Begins", style_section))
    story.append(Paragraph(
        "Three Mile Island / Washington, D.C. \u2014 April\u2013October, 1979",
        style_scene_meta))
    story.append(q(
        "16. The investigation identified five categories of failure. "
        "List and briefly describe each one:", 2))
    story.append(Paragraph("a. Mechanical failure:", style_question))
    story.append(RuledLines(CONTENT_W, 2))
    story.append(Spacer(1, 4))
    story.append(Paragraph("b. Human error:", style_question))
    story.append(RuledLines(CONTENT_W, 2))
    story.append(Spacer(1, 4))
    story.append(Paragraph("c. Training failure:", style_question))
    story.append(RuledLines(CONTENT_W, 2))
    story.append(Spacer(1, 4))
    story.append(Paragraph("d. Regulatory failure:", style_question))
    story.append(RuledLines(CONTENT_W, 2))
    story.append(Spacer(1, 4))
    story.append(Paragraph("e. Communication failure:", style_question))
    story.append(RuledLines(CONTENT_W, 2))
    story.append(Spacer(1, 8))

    story.append(q(
        "YOUR CHOICE: Which failure did you tell the commission to emphasize "
        "(A, B, or C)? Why?", 3, choice=True))

    story.append(ThinHR(CONTENT_W))

    # ════════════════════════════════════════════
    # SECTION 8
    # ════════════════════════════════════════════
    story.append(Paragraph("Scene 8: The Kemeny Commission", style_section))
    story.append(Paragraph(
        "Washington, D.C. \u2014 October 1979", style_scene_meta))
    story.append(q(
        "17. The commission identified a dangerous \u201cmindset\u201d across "
        "the nuclear industry. What was it, and how did it contribute to "
        "the accident?", 4))

    story.append(PageBreak())

    story.append(Paragraph("Scene 8: The Kemeny Commission (continued)", style_section))
    story.append(Spacer(1, 4))
    story.append(q(
        "YOUR CHOICE: What did you tell the commission in your final "
        "assessment (A or B)? Summarize your testimony.", 4, choice=True))

    story.append(ThinHR(CONTENT_W))

    # ════════════════════════════════════════════
    # SECTION 9
    # ════════════════════════════════════════════
    story.append(Paragraph("Scene 9 &amp; Epilogue: The Report", style_section))
    story.append(Paragraph(
        "Washington, D.C. \u2014 October 30, 1979 and beyond", style_scene_meta))
    story.append(q(
        "18. List three specific reforms that resulted from the TMI accident.", 5))
    story.append(q(
        "19. The Kemeny Commission concluded that the physical health effects "
        "of TMI were \u201cnegligible\u201d but the mental health effects were "
        "\u201csignificant and real.\u201d What does this mean? Do you agree "
        "that psychological harm counts as a real consequence of the accident?", 5))
    story.append(q(
        "20. After TMI, no new nuclear power plants were ordered in the "
        "United States for over 30 years. Was this the right response to the "
        "accident, or an overreaction? Explain your reasoning.", 5))

    story.append(PageBreak())

    # ════════════════════════════════════════════
    # FINAL REFLECTION
    # ════════════════════════════════════════════
    story.append(Paragraph("Final Reflection", style_section))
    story.append(Spacer(1, 4))
    story.append(ThinHR(CONTENT_W, color=DARK_BLUE, thickness=1.0))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "In your own words: What is the most important lesson from the "
        "Three Mile Island accident? How does it apply to how we think about "
        "technology, risk, and institutional trust today?",
        ParagraphStyle(
            "ReflectionPrompt", fontName="Helvetica-Bold", fontSize=10.5,
            leading=15, textColor=DARK_BLUE, spaceAfter=6,
        ),
    ))
    story.append(Paragraph(
        "Write a thoughtful response of at least one full paragraph. Consider "
        "the choices you made during the simulation, the evidence you encountered, "
        "and the Kemeny Commission\u2019s conclusions.",
        style_instructions,
    ))
    story.append(Spacer(1, 8))
    story.append(RuledLines(CONTENT_W, 28, line_spacing=23))

    # ── Build ──
    doc.build(story, onFirstPage=page_header_footer,
              onLaterPages=page_header_footer)
    print(f"Created: {path}")


if __name__ == "__main__":
    build_pdf("/Users/ryanbot/Desktop/TMI/TMI_Student_Worksheet.pdf")
