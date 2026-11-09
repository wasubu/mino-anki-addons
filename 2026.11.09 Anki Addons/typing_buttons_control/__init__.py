from aqt import gui_hooks
from aqt.reviewer import Reviewer
from anki.hooks import wrap
import html

# Generate colored feedback comparing typed and correct answers
def compare_answers(correct: str, typed: str) -> str:
    result = []
    min_len = min(len(correct), len(typed))
    has_error = False  # track if any difference found

    for i in range(min_len):
        if typed[i] == correct[i]:
            color = "#a6f3a6"  # green
        else:
            color = "#f8a6a6"  # red
            has_error = True
        result.append(f'<span style="background-color: {color};">{html.escape(typed[i])}</span>')

    # extra typed chars
    if len(typed) > len(correct):
        has_error = True
        for i in range(min_len, len(typed)):
            result.append(f'<span style="background-color: #ccc;">{html.escape(typed[i])}</span>')

    # missing chars
    if len(correct) > len(typed):
        has_error = True
        for i in range(min_len, len(correct)):
            result.append(f'<span style="background-color: #ccc; text-decoration: underline;">{html.escape(correct[i])}</span>')

    joined = ''.join(result)

    arrow_and_correct = ''
    if has_error:
        arrow_and_correct = f'''
        <div style="font-size: 40px; margin-top: 10px;">&#8595;</div>
        <div style="font-size: 40px; margin-top: 5px; color: #222;">
            {html.escape(correct)}
        </div>
        '''

    return f'''
    <div style="text-align: center; margin-top: 20px; font-family: Helvetica, Arial, sans-serif;">
        <div style="font-size: 50px; line-height: 1.4; font-weight: 300; display: inline-block;">
            {joined}
        </div>
        {arrow_and_correct}
    </div>
    '''




# Override typebox answer filter: save correctness & return colored feedback
def new_typeboxAnsAnswerFilter(self, buf: str) -> str:
    if not getattr(self, "typeCorrect", None):  # Skip if not a type answer card
        return buf

    typed_clean = self.typedAnswer.rstrip()
    correct_clean = self.typeCorrect.rstrip()
    correct = (typed_clean == correct_clean)

    # print(f"typeCorrect={self.typeCorrect!r}, typedAnswer={self.typedAnswer!r}, cleanTyped={typed_clean!r}, cleanCorrect={correct_clean!r}, correct={correct}")
    self._typebox_correct = correct

    return compare_answers(correct_clean, typed_clean)

Reviewer.typeboxAnsAnswerFilter = new_typeboxAnsAnswerFilter

# Override answer buttons to show only "Good" or "Again" for type cards
def custom_answer_buttons(self, _old):
    def btn(id: int, label: str) -> str:
        return f'<button class="btn" onclick="pycmd(\'ease{id}\')">{label}</button>'

    # Only apply custom buttons if it’s a type card and has a comparison result
    if hasattr(self, "_typebox_correct") and getattr(self, "typeCorrect", None):
        return btn(3, "Good") if self._typebox_correct else btn(1, "Again")
    else:
        return _old(self)  # fix: pass self

Reviewer._answerButtons = wrap(Reviewer._answerButtons, custom_answer_buttons, "around")

# Clear flag between cards
def on_question_shown(reviewer):
    if hasattr(reviewer, "_typebox_correct"):
        del reviewer._typebox_correct

gui_hooks.reviewer_did_show_question.append(on_question_shown)