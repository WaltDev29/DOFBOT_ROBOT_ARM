#!/usr/bin/env python3
# coding: utf-8
import math

# ==========================================
# 1. 로봇 신체 치수 설정 (단위: cm)
# ==========================================
L1 = 12.0       # 베이스 높이 (바닥 ~ 어깨 관절)
L2 = 8.1        # 상박 길이 (어깨 ~ 팔꿈치)
L3 = 8.1        # 하박 길이 (팔꿈치 ~ 손목)
L_GRIP = 19.0   # 그리퍼 길이 (손목 ~ 끝)

# ==========================================
# 2. 안전 경계값 설정 (매우 중요)
# ==========================================
# 최대 반경: 팔을 다 폈을 때 길이 (8.1 + 8.1 + 19.0 = 35.2cm)
# 안전을 위해 약간 여유를 두어 34cm로 제한
MAX_RADIUS = 34.0 

# 최소 반경: 그리퍼가 너무 길어서 몸통 쪽으로 오면 자기 배를 찌릅니다.
# 중심에서 최소 15cm 이상 떨어져야 안전합니다.
MIN_RADIUS = 15.0 

# 최소 높이: 바닥에 쾅 박지 않도록 설정
MIN_HEIGHT = 2.0

def get_horizontal_distance(x, y):
    """원점(0,0)에서 목표 지점까지의 수평 거리 계산"""
    return math.sqrt(x**2 + y**2)

def check_safety_and_reachability(x, y, z):
    """
    입력된 좌표 (x, y, z)가 로봇이 가기에 안전한지 검사하는 함수
    반환값: (성공여부 True/False, 메시지)
    """
    dist_xy = get_horizontal_distance(x, y)
    
    # [검사 1] 등 뒤(X가 마이너스) 구역 차단
    # 로봇 뒤쪽은 케이블이 꼬이거나 구조적으로 불안정할 수 있어 막습니다.
    if x < 0:
        return False, f"🚫 [위험 구역] 로봇 등 뒤(X<0)로는 갈 수 없습니다. (입력 X={x})"

    # [검사 2] 바닥 충돌 위험
    if z < MIN_HEIGHT:
        return False, f"🚫 [바닥 충돌] 높이가 너무 낮습니다. (입력 Z={z} < 제한 {MIN_HEIGHT})"

    # [검사 3] 몸통 충돌 위험 (너무 가까움)
    # 그리퍼가 길어서 안쪽으로 접으면 로봇 베이스를 찌르게 됩니다.
    if dist_xy < MIN_RADIUS:
        return False, f"🚫 [자해 위험] 몸통과 너무 가깝습니다. (거리 {dist_xy:.1f}cm < 제한 {MIN_RADIUS}cm)"

    # [검사 4] 사거리 초과 (단순 반경)
    if dist_xy > MAX_RADIUS:
        return False, f"🚫 [도달 불가] 거리가 너무 멉니다. 팔이 닿지 않습니다. (거리 {dist_xy:.1f}cm > 한계 {MAX_RADIUS}cm)"

    # [검사 5] 정밀 도달 가능성 계산 (피타고라스)
    # 단순히 반경 안에 있어도, 높이(Z)가 높으면 팔이 안 닿을 수 있습니다.
    
    # 어깨 관절(0, 0, L1)에서 목표 지점까지의 직선 거리 계산
    dist_shoulder_to_tip = math.sqrt(dist_xy**2 + (z - L1)**2)
    
    # 로봇이 물리적으로 뻗을 수 있는 최대 길이 (L2 + L3 + L_GRIP)
    max_physical_reach = L2 + L3 + L_GRIP
    
    if dist_shoulder_to_tip > max_physical_reach:
         return False, f"🚫 [구조적 불가] 반경 내에 있지만, 높이 때문에 팔 길이가 모자랍니다."

    return True, "✅ [안전] 이동 가능한 좌표입니다."

# ==========================================
# 3. 테스트 실행 루프
# ==========================================
if __name__ == "__main__":
    print("========================================")
    print("      DOFBOT 가동 범위 안전 진단기      ")
    print("========================================")
    print(f" * 안전 반경 : {MIN_RADIUS}cm ~ {MAX_RADIUS}cm (몸통 앞쪽)")
    print(f" * 안전 높이 : {MIN_HEIGHT}cm 이상")
    print("========================================")

    while True:
        try:
            print("\n--- 확인하고 싶은 좌표를 입력하세요 (종료는 Ctrl+C) ---")
            in_x = float(input("X 좌표 (cm): "))
            in_y = float(input("Y 좌표 (cm): "))
            in_z = float(input("Z 좌표 (cm): "))

            is_safe, message = check_safety_and_reachability(in_x, in_y, in_z)

            if is_safe:
                print(f"\n{message}")
                print(f"👉 메인 코드에 입력하셔도 좋습니다.")
            else:
                print(f"\n{message}")
                print(f"👉 좌표를 수정해 주세요.")

        except ValueError:
            print("숫자만 입력해 주세요.")
        except KeyboardInterrupt:
            print("\n프로그램을 종료합니다.")
            break