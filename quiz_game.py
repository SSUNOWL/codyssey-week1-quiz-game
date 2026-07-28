"""게임 전체를 관리하는 QuizGame 클래스.

속성: 퀴즈 목록(quizzes), 최고 점수(best_score), 게임 기록(history), 저장 경로(path).
메서드: 메뉴 표시/실행 루프, 퀴즈 풀기/추가/목록/삭제/점수, 파일 저장/불러오기.

이 커밋에서는 '골격'(메뉴 루프 + state.json 로드/세이브)을 만든다.
각 기능(풀기/추가/목록/점수/삭제)은 이후 커밋에서 채운다.
"""

import json
import os

from quiz import Quiz
from default_quizzes import default_quizzes
from helpers import read_int


class QuizGame:
    """퀴즈 게임의 상태와 동작을 모두 담당하는 클래스."""

    DATA_PATH = "state.json"  # 프로젝트 루트에 저장

    def __init__(self, path=DATA_PATH):
        self.path = path
        self.quizzes = []        # list[Quiz]
        self.best_score = 0      # 최고 점수(백분율)
        self.history = []        # 게임 기록 리스트(보너스)
        self.load()              # 시작 시 파일(or 기본 데이터)에서 상태 복원

    # ------------------------------------------------------------------
    # 파일 입출력 (state.json)
    # ------------------------------------------------------------------
    def load(self):
        """state.json에서 상태를 불러온다. 파일이 없으면 기본 퀴즈로 시작."""
        if not os.path.exists(self.path):
            print("📂 저장된 데이터가 없어 기본 퀴즈로 시작합니다.")
            self.quizzes = default_quizzes()
            self.best_score = 0
            self.history = []
            return

        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.quizzes = [Quiz.from_dict(d) for d in data.get("quizzes", [])]
        self.best_score = int(data.get("best_score", 0))
        self.history = list(data.get("history", []))
        if not self.quizzes:  # 파일에 퀴즈가 하나도 없으면 기본으로 보강
            self.quizzes = default_quizzes()
        print(f"📂 저장된 데이터를 불러왔습니다. (퀴즈 {len(self.quizzes)}개, 최고점수 {self.best_score}점)")

    def save(self):
        """현재 상태(퀴즈/최고점수/기록)를 state.json에 UTF-8로 저장."""
        data = {
            "quizzes": [q.to_dict() for q in self.quizzes],
            "best_score": self.best_score,
            "history": self.history,
        }
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------
    # 메뉴 / 실행 루프
    # ------------------------------------------------------------------
    def show_menu(self):
        print("\n" + "=" * 40)
        print("           🎬 나만의 퀴즈 게임 🎬")
        print("=" * 40)
        print(" 1. 퀴즈 풀기")
        print(" 2. 퀴즈 추가")
        print(" 3. 퀴즈 목록")
        print(" 4. 점수 확인")
        print(" 5. 퀴즈 삭제")
        print(" 6. 종료")
        print("=" * 40)

    def run(self):
        """메뉴를 반복 표시하고 사용자의 선택에 따라 기능을 실행한다."""
        while True:
            self.show_menu()
            choice = read_int("선택: ", 1, 6)
            if choice == 1:
                self.play()
            elif choice == 2:
                self.add_quiz()
            elif choice == 3:
                self.list_quizzes()
            elif choice == 4:
                self.show_score()
            elif choice == 5:
                self.delete_quiz()
            elif choice == 6:
                print("\n👋 게임을 종료합니다. 이용해 주셔서 감사합니다!")
                self.save()
                break

    # ------------------------------------------------------------------
    # 기능 메서드 (다음 커밋에서 구현)
    # ------------------------------------------------------------------
    def play(self):
        print("🚧 (준비 중) 퀴즈 풀기 기능은 곧 제공됩니다.")

    def add_quiz(self):
        print("🚧 (준비 중) 퀴즈 추가 기능은 곧 제공됩니다.")

    def list_quizzes(self):
        print("🚧 (준비 중) 퀴즈 목록 기능은 곧 제공됩니다.")

    def show_score(self):
        print("🚧 (준비 중) 점수 확인 기능은 곧 제공됩니다.")

    def delete_quiz(self):
        print("🚧 (준비 중) 퀴즈 삭제 기능은 곧 제공됩니다.")
