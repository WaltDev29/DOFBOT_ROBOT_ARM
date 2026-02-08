import threading
import time
from flask import Flask
from flask_socketio import SocketIO
import shared



app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')



# ====================================
# [WebSocket] 데이터 송출 (Server -> Client)
# ====================================
def broadcast_data():
    while True:
        robot_packet = {}

        with shared.state_lock:
            robot_packet['ee'] = shared.robot_state.copy()
            robot_packet['joints'] = shared.joints_degrees[:]
            robot_packet['gripper'] = shared.gripper_state

        try:
            socketio.emit('robot_state', robot_packet)
        except Exception:
            print("!!! SocketIO Emit Failed")
        
        time.sleep(0.05)



# ====================================
# [WebSocket] 연결 수신
# ====================================
@socketio.on('connect')
def handle_connect():
    print(">>> Client Connected")

# ====================================
# [WebSocket] 제어 명령 수신
# ====================================
# ============ Joint ============
@socketio.on('set_joints')
def handle_set_joints(data):
    if 'joints' in data:
        with shared.cmd_lock:
            shared.command["joint_cmd"] = data['joints']

# ============ 목표 좌표 ============
@socketio.on('set_pos')
def handle_set_pos(data):
    if 'pos' in data:
        with shared.cmd_lock:
            shared.command["target_pos"] = data['pos']
            
# ============ Gripper ============
@socketio.on('set_gripper')
def handle_set_gripper(data):
    if 'gripper' in data:
        with shared.cmd_lock:
            shared.command["gripper_cmd"] = data['gripper']

# ============ POST 로봇 힘 ============
@socketio.on('set_force')
def handle_set_force(data):
    if "force" in data:
        with shared.cmd_lock:
            shared.command["force"] = data["force"]

# ============ 최대 속도 ============
@socketio.on('set_max_velocity')
def handle_set_max_velocity(data):
    if 'max_velocity' in data:
        with shared.cmd_lock:
            shared.command["max_velocity"] = data['max_velocity']



# ====================================
# 서버 실행 함수
# ====================================
def run_flask():
    print(">>> Flask SocketIO Server Started on port 5000 (Threading Mode)")
    
    # 데이터 전송 백그라운드 스레드 시작
    t = threading.Thread(target=broadcast_data, daemon=True)
    t.start()
    
    # allow_unsafe_werkzeug=True 옵션 추가
    socketio.run(app, host="0.0.0.0", port=5000, debug=False, use_reloader=False, allow_unsafe_werkzeug=True)