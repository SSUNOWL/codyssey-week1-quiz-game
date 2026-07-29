"""사용자 입력을 안전하게 받기 위한 공통 함수 모음.

과제의 '공통 입력/예외 처리 기준'을 한 곳에 모아 메뉴 선택·문제 수·삭제 번호·퀴즈 추가 등에서
재사용한다. (정답 입력은 'h' 힌트도 받아야 해 quiz_game._read_answer에서 같은 규칙을 별도로 적용.) 처리 규칙:
  - 입력 앞뒤 공백은 제거한다.
  - 빈 입력(그냥 Enter)          -> 안내 후 재입력
  - 숫자 변환 실패(예: 'abc')     -> 안내 후 재입력
  - 허용 범위 밖(예: 메뉴 9)      -> 안내 후 재입력

주의: Ctrl+C(KeyboardInterrupt)와 입력 종료(EOFError)는 여기서 잡지 않고
그대로 위로 전달한다. 프로그램 전체의 안전 종료는 main.py에서 처리한다.
"""


def read_int(prompt, low, high):
    """low~high 범위의 정수를 받을 때까지 반복해서 물어보고, 유효한 정수를 반환한다."""
    while True:
        raw = input(prompt).strip()  # 앞뒤 공백 제거
        if raw == "":
            print(f"⚠️  빈 입력입니다. {low}~{high} 사이의 숫자를 입력하세요.")
            continue
        try:
            value = int(raw)
        except ValueError:
            print(f"⚠️  숫자가 아닙니다. {low}~{high} 사이의 숫자를 입력하세요.")
            continue
        if not low <= value <= high:
            print(f"⚠️  범위를 벗어났습니다. {low}~{high} 사이의 숫자를 입력하세요.")
            continue
        return value


def read_nonempty(prompt):
    """빈 문자열이 아닌 텍스트를 받을 때까지 반복하고, 공백을 제거한 문자열을 반환한다."""
    while True:
        text = input(prompt).strip()
        if text == "":
            print("⚠️  빈 값은 입력할 수 없습니다. 다시 입력하세요.")
            continue
        return text


def read_menu_choice(prompt, low, high):
    """메뉴 선택 전용 입력.

    'h'(힌트)처럼 숫자가 아닌 특수 입력을 다루지 않는 순수 메뉴용이며,
    내부적으로 read_int를 그대로 사용한다.
    """
    return read_int(prompt, low, high)
