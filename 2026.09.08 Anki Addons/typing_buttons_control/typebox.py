import html
import re
from anki.hooks import wrap
from aqt import gui_hooks
from aqt.reviewer import Reviewer

Reviewer.typeboxAnsPat = r"\[\[typebox:(.*?)\]\]"


def typeboxAnsFilter(self, buf: str) -> str:
    if self.state == "question":
        self._typebox_note = False
        typebox_replaced = self.typeboxAnsQuestionFilter(buf)
        if typebox_replaced != buf:
            self._typebox_note = True
            return typebox_replaced
        return self.typeAnsQuestionFilter(buf)

    elif hasattr(self, "_typebox_note") and self._typebox_note:
        self._typebox_note = False
        return self.typeboxAnsAnswerFilter(buf)

    return self.typeAnsAnswerFilter(buf)


def typeboxAnsQuestionFilter(self, buf: str) -> str:
    self.typeCorrect = None
    m = re.search(self.typeboxAnsPat, buf)
    if not m:
        return buf

    fld = m.group(1)
    fields = self.card.model()["flds"]
    for f in fields:
        if f["name"] == fld:
            self.typeCorrect = self.card.note()[f["name"]]
            self.typeFont = f.get("font", "Arial")
            self.typeSize = f.get("size", 20)
            break

    if not self.typeCorrect:
        maybe_answer_field = next((f for f in fields if f["name"] == "Back"), fields[-1])
        self.typeFont = maybe_answer_field.get("font", "Arial")
        self.typeSize = maybe_answer_field.get("size", 20)

    return re.sub(
        self.typeboxAnsPat,
        f"""
<center>
<textarea id=typeans class=textbox-input onkeypress="typeboxAns();" style="font-family: '{self.typeFont}'; font-size: {self.typeSize}px;"></textarea>
</center>
<script>
function typeboxAns() {{
    if (window.event.keyCode == 13 && window.event.ctrlKey) pycmd("ans");
}}
</script>
""",
        buf,
    )


# Generate colored feedback comparing typed and correct answers
def compare_answers(correct: str, typed: str) -> str:
    result = []
    min_len = min(len(correct), len(typed))
    has_error = False

    for i in range(min_len):
        if typed[i] == correct[i]:
            color = "#a6f3a6"
        else:
            color = "#f8a6a6"
            has_error = True
        result.append(
            f'<span style="background-color: {color};">{html.escape(typed[i])}</span>'
        )

    if len(typed) > len(correct):
        has_error = True
        for i in range(min_len, len(typed)):
            result.append(
                f'<span style="background-color: #ccc;">{html.escape(typed[i])}</span>'
            )

    if len(correct) > len(typed):
        has_error = True
        for i in range(min_len, len(correct)):
            result.append(
                f'<span style="background-color: #ccc; text-decoration: underline;">{html.escape(correct[i])}</span>'
            )

    joined = "".join(result)
    arrow_and_correct = ""

    if has_error:
        arrow_and_correct = f"""
        <div style="font-size: 40px; margin-top: 10px;">&#8595;</div>
        <div style="font-size: 40px; margin-top: 5px; color: #222;">
            {html.escape(correct)}
        </div>
        """

    return f"""
    <div style="text-align: center; margin-top: 20px; font-family: Helvetica, Arial, sans-serif;">
        <div style="font-size: 50px; line-height: 1.4; font-weight: 300; display: inline-block;">
            {joined}
        </div>
        {arrow_and_correct}
    </div>
    """


def new_typeboxAnsAnswerFilter(self, buf: str) -> str:
    if not getattr(self, "typeCorrect", None):
        return buf

    typed_clean = (getattr(self, "typedAnswer", "") or "").rstrip()
    correct_clean = (self.typeCorrect or "").rstrip()
    correct = typed_clean == correct_clean

    self._typebox_correct = correct
    return compare_answers(correct_clean, typed_clean)


def custom_answer_buttons(self, _old):
    def btn(id: int, label: str) -> str:
        return f'<button class="btn" onclick="pycmd(\'ease{id}\')">{label}</button>'

    if hasattr(self, "_typebox_correct") and getattr(self, "typeCorrect", None):
        return btn(3, "Good") if self._typebox_correct else btn(1, "Again")
    else:
        return _old(self)


# Intercept keypress actions (Space/Enter) to enforce correctness
_old_answerCard = Reviewer._answerCard


def _typebox_safe_answerCard(self, ease):
    if hasattr(self, "_typebox_correct") and getattr(self, "typeCorrect", None):
        ease = 3 if self._typebox_correct else 1
    return _old_answerCard(self, ease)


def on_question_shown(reviewer):
    if hasattr(reviewer, "_typebox_correct"):
        del reviewer._typebox_correct


def setup():
    """Initializes hooks and method overrides when loaded by __init__.py."""
    Reviewer.typeAnsFilter = typeboxAnsFilter
    Reviewer.typeboxAnsQuestionFilter = typeboxAnsQuestionFilter
    Reviewer.typeboxAnsAnswerFilter = new_typeboxAnsAnswerFilter
    Reviewer._answerCard = _typebox_safe_answerCard
    Reviewer._answerButtons = wrap(
        Reviewer._answerButtons, custom_answer_buttons, "around"
    )
    gui_hooks.reviewer_did_show_question.append(on_question_shown)