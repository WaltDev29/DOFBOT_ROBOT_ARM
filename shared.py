import threading



# ============ 동기화 Lock ============
state_lock = threading.Lock()
cmd_lock = threading.Lock()



# ============ 로봇 정보 (Robot -> Flask) ============
robot_state = {"x": 0.0, "y": 0.0, "z": 0.0}
joints_degrees = [0, 0, 0, 0, 0]
gripper_state = 0



# ============ 제어 명령 (Flask -> Robot) ============
command = {
    "target_pos": None, # IK 목표 좌표 [x, y, z]
    "joint_cmd": None,  # Joint 각도 [deg1, deg2, deg3, deg4, deg5]
    "gripper_cmd": None, # Gripper 제어 0.0 ~ 0.06
    "force": 100,       # 로봇 힘 int
    "max_velocity": 100,  # 로봇 최대 속도 int
}
