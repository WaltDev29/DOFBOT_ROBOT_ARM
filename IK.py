
import math
import time
from Arm_Lib import Arm_Device

Arm = Arm_Device()
time.sleep(0.1)

L1 = 12.0
L2 = 8.1
L3 = 8.1
L_GRIP = 19.0

OFFSET_J1 = 0
OFFSET_J2 = 0
OFFSET_J3 = 180
OFFSET_J4 = 90

FIXED_J5 = 90
FIXED_J6 = 180

def calculate_angles(x, y, z, try_pitch_deg):
    try:
        theta1 = math.degrees(math.atan2(y, x))
        pitch_rad = math.radians(try_pitch_deg)
        horizontal_dist_total = math.sqrt(x**2 + y**2)
        
        r_wrist = horizontal_dist_total - L_GRIP * math.cos(pitch_rad)
        z_wrist = z - L_GRIP * math.sin(pitch_rad) - L1
        
        dist_shoulder_to_wrist = math.sqrt(r_wrist**2 + z_wrist**2)
        
        if dist_shoulder_to_wrist > (L2 + L3) or dist_shoulder_to_wrist < abs(L2 - L3):
            return None

        cos_angle_shoulder = (L2**2 + dist_shoulder_to_wrist**2 - L3**2) / (2 * L2 * dist_shoulder_to_wrist)
        cos_angle_elbow = (L2**2 + L3**2 - dist_shoulder_to_wrist**2) / (2 * L2 * L3)
        
        cos_angle_shoulder = max(min(cos_angle_shoulder, 1.0), -1.0)
        cos_angle_elbow = max(min(cos_angle_elbow, 1.0), -1.0)

        alpha = math.acos(cos_angle_shoulder)
        beta = math.acos(cos_angle_elbow)
        base_elevation = math.atan2(z_wrist, r_wrist)

        theta2 = math.degrees(base_elevation + alpha)
        theta3 = -math.degrees(math.pi - beta)
        theta4 = try_pitch_deg - (theta2 + theta3)
        
        return (theta1, theta2, theta3, theta4, try_pitch_deg)
    except:
        return None

def solve_ik_auto(x, y, z):
    best_solution = None
    min_deviation = 9999
    
    for p in range(-45, 46, 5): 
        result = calculate_angles(x, y, z, p)
        if result:
            t1, t2, t3, t4, _ = result
            s1 = t1 + OFFSET_J1
            s2 = t2 + OFFSET_J2
            s3 = t3 + OFFSET_J3
            s4 = t4 + OFFSET_J4
            
            if (0 <= s1 <= 180) and (0 <= s2 <= 180) and (0 <= s3 <= 180) and (0 <= s4 <= 180):
                deviation = abs(s4 - 0) 
                if deviation < min_deviation:
                    min_deviation = deviation
                    best_solution = (int(s1), int(s2), int(s3), int(s4))
    return best_solution

def get_linear_path(start_pos, end_pos, steps=10):
    path_servos = []
    x1, y1, z1 = start_pos
    x2, y2, z2 = end_pos
    
    for i in range(steps + 1):
        t = i / steps
        cx = x1 + (x2 - x1) * t
        cy = y1 + (y2 - y1) * t
        cz = z1 + (z2 - z1) * t

        servos = solve_ik_auto(cx, cy, cz)
        if servos:
            path_servos.append(servos)
        else:
            return None
    return path_servos

def generate_box_points(center_pos, size):
    cx, cy, cz = center_pos
    hs = size / 2.0 
    
    p1 = (cx - hs, cy - hs, cz - hs) 
    p2 = (cx + hs, cy - hs, cz - hs) 
    p3 = (cx + hs, cy + hs, cz - hs) 
    p4 = (cx - hs, cy + hs, cz - hs) 
    
    #p5 = (cx - hs, cy - hs, cz - hs - size) 
    #p6 = (cx + hs, cy - hs, cz - hs - size) 
    #p7 = (cx + hs, cy + hs, cz - hs - size) 
    #p8 = (cx - hs, cy + hs, cz - hs - size) 
    
    return [p1, p2, p3, p4, p1]

def run_path(full_path_angles):
    for i, angles in enumerate(full_path_angles):
        s1, s2, s3, s4 = angles
        Arm.Arm_serial_servo_write6(s1, s2, s3, s4, FIXED_J5, FIXED_J6, 100)
        time.sleep(0.1)

if __name__ == "__main__":
    try:
        Arm.Arm_serial_servo_write6(90, 90, 90, 90, 90, 180, 1000)
        time.sleep(1.5)

        CENTER_POINT = (0.0, 20.0, 10.0) 
        BOX_SIZE = 8.0 

        print(f"Center: {CENTER_POINT}, Size: {BOX_SIZE}")
        
        waypoints = generate_box_points(CENTER_POINT, BOX_SIZE)
        full_trajectory = []
        
        for i in range(len(waypoints) - 1):
            start = waypoints[i]
            end = waypoints[i+1]
            
            segment = get_linear_path(start, end, steps=10)
            if segment:
                full_trajectory.extend(segment)
            else:
                print(f"Error: Cannot reach from {start} to {end}")
                exit()
        
        print(f"Path calculated. Press Enter to Draw Box.")
        input()
        
        start_angles = full_trajectory[0]
        Arm.Arm_serial_servo_write6(start_angles[0], start_angles[1], start_angles[2], start_angles[3], FIXED_J5, FIXED_J6, 1500)
        time.sleep(2)
        
        run_path(full_trajectory)
        print("Done.")

    except KeyboardInterrupt:
        print("Stopped.")
