"""게임 전체를 관리하는 QuizGame 클래스.

속성: 퀴즈 목록(quizzes), 최고 점수(best_score), 게임 기록(history), 저장 경로(path).
메서드: 메뉴 표시/실행 루프, 퀴즈 풀기/추가/목록/삭제/점수, 파일 저장/불러오기.
"""

import json
import os
import random
from datetime import datetime

from quiz import Quiz
from default_quizzes import default_quizzes
from helpers import read_int, read_nonempty


class QuizGame:
    """퀴즈 게임의 상태와 동작을 모두 담당하는 클래스."""

    DATA_PATH = "state.json"      # 프로젝트 루트에 저장
    BACKUP_SUFFIX = ".bak"        # 백업 파일은 state.json.bak

    def __init__(self, path=DATA_PATH):
        self.path = path
        self.backup_path = path + self.BACKUP_SUFFIX
        self.quizzes = []        # list[Quiz]
        self.best_score = None   # 최고 점수(백분율). None = 아직 안 풀었음
        self.history = []        # 게임 기록 리스트(보너스)
        self.load()              # 시작 시 파일(or 기본 데이터)에서 상태 복원

    # ------------------------------------------------------------------
    # 파일 입출력 (state.json)
    # ------------------------------------------------------------------
    def _use_defaults(self):
        """상태를 기본 퀴즈로 초기화(파일 없음/손상 시 공통 사용)."""
        self.quizzes = default_quizzes()
        self.best_score = None
        self.history = []

    def _read_state(self, path):
        """path에서 상태를 읽어 (퀴즈 목록, 최고 점수, 기록)으로 돌려준다.

        내용이 조금이라도 어긋나면 예외를 그대로 낸다. '어디까지 믿을 수 있는지'를
        판단하는 곳은 여기 한 곳이고, 실패했을 때 무엇으로 대체할지는 load()가 정한다.
        """
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            # 최상위가 객체가 아니면(예: [] 또는 null) 손상으로 간주 → load()의 except가 받는다
            raise ValueError("최상위 구조가 객체(dict)가 아닙니다")
        quizzes = [Quiz.from_dict(d) for d in data.get("quizzes", [])]
        raw_best = data.get("best_score", None)
        best_score = int(raw_best) if isinstance(raw_best, (int, float)) else None
        history = list(data.get("history", []))
        return quizzes, best_score, history

    def load(self):
        """상태를 복원한다. 본 파일 → 백업 파일 → 기본 퀴즈 순으로 시도한다.

        - 두 파일이 모두 없으면(첫 실행) 기본 퀴즈로 시작한다.
        - 본 파일이 손상되면 백업(state.json.bak)으로 복구를 시도한다.
        - 둘 다 손상되어도 기본 퀴즈가 코드에 내장되어 있으므로 게임은 항상 시작된다.
        """
        if not os.path.exists(self.path) and not os.path.exists(self.backup_path):
            print("📂 저장된 데이터가 없어 기본 퀴즈로 시작합니다.")
            self._use_defaults()
            return

        for path, label in ((self.path, "데이터 파일"), (self.backup_path, "백업 파일")):
            if not os.path.exists(path):
                continue
            try:
                # 셋 다 성공했을 때만 한꺼번에 대입된다(중간에 실패하면 상태가 반쯤 덮이지 않음).
                self.quizzes, self.best_score, self.history = self._read_state(path)
            except (json.JSONDecodeError, OSError, ValueError, KeyError, TypeError) as error:
                print(f"⚠️  {label}이 손상되었습니다. (원인: {error})")
                continue
            if not self.quizzes:  # 파일은 멀쩡한데 퀴즈가 0개면 빈 게임이 되므로 기본값으로
                self.quizzes = default_quizzes()
            if path == self.backup_path:
                print("♻️  백업 파일에서 복구했습니다.")
            print(f"📂 저장된 데이터를 불러왔습니다. (퀴즈 {len(self.quizzes)}개, 최고점수 {self.best_score_text()})")
            return

        print("⚠️  데이터 파일과 백업 파일이 모두 손상되어 기본 퀴즈로 복구합니다.")
        self._use_defaults()

    def save(self):
        """현재 상태를 state.json에, 같은 내용을 state.json.bak에 UTF-8로 저장.

        백업에는 방금 검증된 메모리 상태만 기록되므로, 손상된 내용이 백업으로 번지지 않는다.
        """
        data = {
            "quizzes": [q.to_dict() for q in self.quizzes],
            "best_score": self.best_score,
            "history": self.history,
        }
        text = json.dumps(data, ensure_ascii=False, indent=2)
        try:
            for path in (self.path, self.backup_path):
                with open(path, "w", encoding="utf-8") as f:
                    f.write(text)
        except OSError as error:
            print(f"⚠️  저장 중 오류가 발생했습니다: {error}")

    def best_score_text(self):
        """최고 점수를 사람이 읽기 좋은 문자열로. 아직 안 풀었으면 '아직 없음'."""
        return "아직 없음" if self.best_score is None else f"{self.best_score}점"

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
    # 기능 메서드 (풀기 / 추가 / 목록 / 점수 / 삭제)
    # ------------------------------------------------------------------
    def _read_answer(self, quiz):
        """정답(1~4) 또는 힌트('h')를 입력받는다.

        반환값: (선택한 번호, 힌트 사용 여부)
        힌트를 보면 used_hint=True가 되어 해당 문제는 점수에 포함되지 않는다(점수 차감).
        """
        used_hint = False
        while True:
            raw = input("정답 입력 (1-4, 힌트는 h): ").strip().lower()
            if raw == "":
                print("⚠️  빈 입력입니다. 1-4 숫자 또는 h를 입력하세요.")
                continue
            if raw == "h":  # 보너스: 힌트
                if quiz.has_hint():
                    print(f"💡 힌트: {quiz.hint}  (힌트를 보면 이 문제는 점수에서 제외됩니다)")
                    used_hint = True
                else:
                    print("ℹ️  이 문제에는 힌트가 없습니다.")
                continue
            try:
                value = int(raw)
            except ValueError:
                print("⚠️  숫자가 아닙니다. 1-4 숫자 또는 h를 입력하세요.")
                continue
            if not 1 <= value <= Quiz.CHOICE_COUNT:
                print(f"⚠️  1-{Quiz.CHOICE_COUNT} 사이의 숫자를 입력하세요.")
                continue
            return value, used_hint

    def play(self):
        """퀴즈를 출제한다. (보너스: 문제 수 선택 + 랜덤 출제 + 힌트 + 기록 저장)"""
        if not self.quizzes:
            print("\n😢 아직 등록된 퀴즈가 없습니다. 먼저 '퀴즈 추가'로 문제를 만들어 주세요.")
            return

        available = len(self.quizzes)
        # 보너스 1) 문제 수 선택
        count = read_int(f"\n몇 문제를 풀까요? (1-{available}): ", 1, available)
        # 보너스 2) 랜덤 출제: 무작위로 count개를 뽑아 순서도 섞는다
        selected = random.sample(self.quizzes, count)

        print(f"\n📝 퀴즈를 시작합니다! (총 {count}문제, 무작위 출제)")
        correct = 0
        for number, quiz in enumerate(selected, start=1):
            print("\n" + "-" * 40)
            print(quiz.render(number))
            choice, used_hint = self._read_answer(quiz)
            is_right = quiz.is_correct(choice)
            if is_right and not used_hint:
                print("✅ 정답입니다!")
                correct += 1
            elif is_right:
                print("✅ 정답이지만 힌트를 사용해 이 문제는 점수에 포함되지 않습니다.")
            else:
                print(f"❌ 오답입니다. 정답은 {quiz.answer}번입니다.")

        score = int(correct / count * 100)  # 백분율 점수
        print("\n" + "=" * 40)
        print(f"🏆 결과: {count}문제 중 {correct}문제 정답! ({score}점)")
        if self.best_score is None or score > self.best_score:
            self.best_score = score
            print("🎉 새로운 최고 점수입니다!")
        else:
            print(f"   (현재 최고 점수: {self.best_score_text()})")
        print("=" * 40)

        # 보너스 5) 점수 기록 히스토리: 날짜/시간·문제 수·정답 수·점수 저장
        self.history.append({
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total": count,
            "correct": correct,
            "score": score,
        })
        self.save()  # 최고 점수·기록을 파일에 반영

    def add_quiz(self):
        """사용자에게 문제·선택지 4개·정답 번호(+힌트)를 받아 새 퀴즈를 등록하고 저장한다."""
        print("\n📌 새로운 퀴즈를 추가합니다.")
        question = read_nonempty("문제를 입력하세요: ")
        choices = [read_nonempty(f"선택지 {i}: ") for i in range(1, Quiz.CHOICE_COUNT + 1)]
        answer = read_int(f"정답 번호 (1-{Quiz.CHOICE_COUNT}): ", 1, Quiz.CHOICE_COUNT)
        hint = input("힌트 (없으면 그냥 Enter): ").strip()  # 힌트는 선택 입력

        try:
            quiz = Quiz(question, choices, answer, hint)
        except ValueError as error:
            # 이론상 위 입력 검증을 통과하지만, 방어적으로 한 번 더 확인한다.
            print(f"⚠️  퀴즈를 만들 수 없습니다: {error}")
            return

        self.quizzes.append(quiz)
        self.save()
        print("✅ 퀴즈가 추가되었습니다!")

    def list_quizzes(self):
        """등록된 모든 퀴즈의 문제 지문을 번호와 함께 보여준다."""
        if not self.quizzes:
            print("\n📋 등록된 퀴즈가 없습니다. '퀴즈 추가'로 문제를 만들어 보세요.")
            return
        print(f"\n📋 등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        print("-" * 40)
        for number, quiz in enumerate(self.quizzes, start=1):
            print(f"[{number}] {quiz.question}")
        print("-" * 40)

    def show_score(self):
        """최고 점수를 보여준다. 아직 한 번도 풀지 않았으면 안내한다."""
        if self.best_score is None:
            print("\n🏆 아직 퀴즈를 풀지 않았습니다. '퀴즈 풀기'로 최고 점수에 도전해 보세요!")
            return
        print(f"\n🏆 최고 점수: {self.best_score_text()}")
        # 보너스 5) 최근 게임 기록(최대 5개) 표시
        if self.history:
            print("\n📜 최근 기록")
            print("-" * 40)
            for record in self.history[-5:]:
                print(f"  {record['datetime']}  |  "
                      f"{record['total']}문제 중 {record['correct']}개 정답  |  {record['score']}점")
            print("-" * 40)

    def delete_quiz(self):
        """보너스: 목록에서 번호를 골라 퀴즈를 삭제하고 파일에 반영한다."""
        if not self.quizzes:
            print("\n🗑️  삭제할 퀴즈가 없습니다.")
            return
        self.list_quizzes()
        number = read_int(f"삭제할 퀴즈 번호 (1-{len(self.quizzes)}): ", 1, len(self.quizzes))
        removed = self.quizzes.pop(number - 1)
        self.save()
        print(f"🗑️  삭제되었습니다: {removed.question}")
