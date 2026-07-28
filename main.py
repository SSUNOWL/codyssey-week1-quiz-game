"""프로그램 진입점.

- 표준 출력/입력을 UTF-8로 맞춰 한글·이모지가 깨지지 않게 한다(윈도우 대비).
- QuizGame을 생성하고 메뉴 루프를 실행한다.
- Ctrl+C(KeyboardInterrupt)나 입력 종료(EOFError)가 발생해도 '비정상 종료'하지 않도록
  안내 메시지를 출력하고 가능한 범위에서 저장한 뒤 안전하게 종료한다.

실행: python main.py
"""

import sys

from quiz_game import QuizGame


def _enable_utf8():
    """콘솔 인코딩을 UTF-8로 재설정(지원되지 않는 환경이면 조용히 무시)."""
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass


def main():
    _enable_utf8()
    game = QuizGame()
    try:
        game.run()
    except (KeyboardInterrupt, EOFError):
        # 강제 종료 신호가 와도 데이터를 지키고 깔끔하게 끝낸다.
        print("\n\n⚠️  입력이 중단되었습니다. 저장 후 안전하게 종료합니다.")
        game.save()


if __name__ == "__main__":
    main()
