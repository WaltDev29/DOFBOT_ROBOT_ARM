import threading
import robot_thread
import server


if __name__ == "__main__":
    print(">>> System Starting...")

    t_robot = threading.Thread(target=robot_thread.run_robot_loop, daemon=True)
    t_robot.start()
    
    #with shared.cmd_lock:
        #shared.command["gripper_cmd"] = 100
        #shared.command["target_pos"] = {"x": 0.10, "y": 0.10, "z": 0.10}
        #print(shared.command["gripper_cmd"]) 
        #print(shared.command["target_pos"])

    server.run_flask()