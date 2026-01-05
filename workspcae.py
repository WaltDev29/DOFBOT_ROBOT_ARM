import math


# 1. 로봇 설정

L1 = 12.0       # 베이스 높이
L2 = 8.1        # 상박
L3 = 8.1        # 하박
L_GRIP = 19.0   # 그리퍼 길이

# 안전 제약 조건
MAX_RADIUS = 34.0  # 최대 반경
MIN_RADIUS = 15.0  # 최소 반경 (몸통 충돌 방지)
MIN_HEIGHT = 2.0   # 바닥 충돌 방지 높이

def check_safety_and_reachability(x, y, z):
    """좌표 유효성 검사 함수 (Safety Check와 동일)"""
    dist_xy = math.sqrt(x**2 + y**2)
    
    # 1. 등 뒤 금지
    if x < 0: return False
    # 2. 바닥 충돌
    if z < MIN_HEIGHT: return False
    # 3. 몸통 충돌 (너무 가까움)
    if dist_xy < MIN_RADIUS: return False
    # 4. 최대 반경 초과
    if dist_xy > MAX_RADIUS: return False

    # 5. 높이를 포함한 실제 팔 길이 도달 가능성 체크
    # 어깨(0,0,L1)에서 목표점까지의 직선 거리
    dist_shoulder_to_tip = math.sqrt(dist_xy**2 + (z - L1)**2)
    max_physical_reach = L2 + L3 + L_GRIP
    
    if dist_shoulder_to_tip > max_physical_reach:
        return False

    return True


# 2. 작업 영역 스캔 (Main Calculation)

def calculate_workspace_limits():
    
    # 3D 공간 스캔 범위 설정 (cm 단위)
    # 넉넉하게 잡고 safe 함수로 걸러냅니다.
    scan_range = range(-40, 40) # X, Y, Z 탐색 범위
    
    valid_points = []
    
    # 1cm 간격으로 전수 조사
    for x in range(0, 40): # X는 앞쪽(양수)만 사용
        for y in scan_range:
            for z in range(0, 40):
                if check_safety_and_reachability(x, y, z):
                    valid_points.append((x, y, z))

    if not valid_points:
        print("❌ 유효한 작업 공간을 찾을 수 없습니다. 제약 조건을 확인하세요.")
        return

    # Min/Max 추출
    xs = [p[0] for p in valid_points]
    ys = [p[1] for p in valid_points]
    zs = [p[2] for p in valid_points]

    print("\n사용 가능한 좌표 범위\n")
    
    print(f"📍 X축 (앞뒤): {min(xs)} cm ~ {max(xs)} cm")
    print(f"📍 Y축 (좌우): {min(ys)} cm ~ {max(ys)} cm")
    print(f"📍 Z축 (높이): {min(zs)} cm ~ {max(zs)} cm\n")

    print("주의: 이 값은 '최대 외곽선(Bounding Box)'입니다.")
    print("   도넛 모양이므로 X가 최소일 때 Y는 최대가 될 수 없습니다.")
    print("   안전하게 쓰려면 '중간값'을 기준으로 사용하세요.\n")

if __name__ == "__main__":
    calculate_workspace_limits()