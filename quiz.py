"""개별 퀴즈 한 문제를 표현하는 Quiz 클래스.

한 문제는 '문제 지문(question)', '선택지 4개(choices)', '정답 번호(answer, 1~4)',
그리고 보너스용 '힌트(hint)'로 이루어진다. 데이터 저장/불러오기를 위해
dict <-> Quiz 변환 메서드(to_dict / from_dict)를 함께 제공한다.
"""


class Quiz:
    """퀴즈 한 문제. 문제·선택지·정답·힌트를 속성으로 가진다."""

    CHOICE_COUNT = 4  # 선택지는 4개로 고정

    def __init__(self, question, choices, answer, hint=""):
        # --- 유효성 검사: 손상된 데이터로부터 게임을 보호한다 ---
        question = str(question).strip()
        if not question:
            raise ValueError("문제(question)는 비어 있을 수 없습니다.")
        if not isinstance(choices, (list, tuple)) or len(choices) != self.CHOICE_COUNT:
            raise ValueError(f"선택지(choices)는 정확히 {self.CHOICE_COUNT}개여야 합니다.")
        choices = [str(c).strip() for c in choices]
        if any(c == "" for c in choices):
            raise ValueError("선택지에는 빈 값이 있을 수 없습니다.")
        answer = int(answer)  # 문자열로 들어와도 int로 변환 (실패 시 ValueError)
        if not 1 <= answer <= self.CHOICE_COUNT:
            raise ValueError(f"정답(answer)은 1~{self.CHOICE_COUNT} 사이여야 합니다.")

        self.question = question
        self.choices = choices
        self.answer = answer          # 정답은 1~4 번호로 관리
        self.hint = str(hint).strip()  # 힌트가 없으면 빈 문자열

    def render(self, index):
        """문제 번호(index)와 지문·선택지를 보기 좋은 문자열로 만들어 돌려준다."""
        lines = [f"[문제 {index}]", self.question, ""]
        for i, choice in enumerate(self.choices, start=1):
            lines.append(f"  {i}. {choice}")
        return "\n".join(lines)

    def is_correct(self, choice):
        """사용자가 고른 번호(choice)가 정답과 같으면 True."""
        return int(choice) == self.answer

    def has_hint(self):
        """힌트가 등록되어 있으면 True."""
        return bool(self.hint)

    # --- JSON 저장/불러오기용 변환 ---
    def to_dict(self):
        """Quiz 객체를 JSON에 저장 가능한 dict로 변환."""
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
            "hint": self.hint,
        }

    @classmethod
    def from_dict(cls, data):
        """dict(파일에서 읽은 한 문제)를 Quiz 객체로 복원."""
        return cls(
            question=data["question"],
            choices=data["choices"],
            answer=data["answer"],
            hint=data.get("hint", ""),  # 예전 데이터에 hint가 없어도 안전
        )
