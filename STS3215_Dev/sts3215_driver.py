import requests
import time

# === CONFIGURATION ===
ESP_IP = "http://192.168.137.196"
TIMEOUT = 0.5

def _send_request(endpoint, params):
    """Helper function to handle HTTP requests cleanly."""
    try:
        url = f"{ESP_IP}/{endpoint}"
        resp = requests.get(url, params=params, timeout=TIMEOUT)
        if resp.status_code == 200:
            return resp.json() if resp.headers.get('content-type', '').startswith('application/json') else resp.text
        else:
            print(f"[ERR] Request to /{endpoint} failed with status {resp.status_code}")
            return None
    except Exception as e:
        print(f"[ERR] Connection issue on /{endpoint}: {e}")
        return None


# === CORE SERVO FUNCTIONS ===

def move(id, pos, speed=800, acc=50):
    """
    Moves a servo to a specific raw position.
    :param id: Servo ID (int)
    :param pos: Target position (typically 0 - 4095)
    :param speed: Steps per second
    :param acc: Acceleration (0 - 254)
    """
    params = {"id": id, "pos": int(pos), "spd": speed, "acc": acc}
    res = _send_request("move", params)
    if res is not None:
        print(f"[OK] Move ID:{id} -> Position: {pos}")

def move_angle(id, angle_deg, speed=800, acc=50):
    """
    Convenience function to move a servo using degrees (0° - 360°).
    """
    pos = int(((180 - angle_deg)/ 360.0) * 4095)
    move(id, pos, speed, acc)

def set_torque(id, enable=True):
    """Enable or disable servo torque."""
    val = 1 if enable else 0
    _send_request("torque", {"id": id, "en": val})
    print(f"[OK] Torque ID:{id} -> {'ENABLED' if enable else 'DISABLED'}")

def set_multiturn(id, enable=True):
    """Enable or disable multi-turn mode (removes 0-4095 position limits)."""
    val = 1 if enable else 0
    _send_request("multiturn", {"id": id, "en": val})
    print(f"[OK] Multi-turn ID:{id} -> {'ENABLED' if enable else 'DISABLED'}")

def set_mode(id, mode):
    """
    Set servo operating mode.
    mode 0 = Position Control (Servo Mode)
    mode 3 = Continuous Rotation (Motor Mode)
    """
    _send_request("mode", {"id": id, "val": mode})
    print(f"[OK] Mode ID:{id} set to {mode}")

def set_gripper(angle):
    """
    Control the end-effector gripper (SG90).
    :param angle: 0 to 180 degrees
    """
    _send_request("gripper", {"pos": angle})
    print(f"[OK] Gripper set to {angle}°")


# === STATUS & FEEDBACK ===

def get_status(id):
    """
    Returns a dictionary containing servo feedback: pos, volt, temp, load, etc.
    """
    data = _send_request("feedback", {"id": id})
    return data if isinstance(data, dict) else None

def print_servo_status(id):
    """Print formatted diagnostic info for a specific servo."""
    status = get_status(id)
    if status:
        print(f"\n--- SERVO {id} STATUS ---")
        print(f"Position: {status.get('pos')}")
        print(f"Voltage:  {status.get('volt')} V")
        print(f"Temp:     {status.get('temp')} °C")
        print(f"Load:     {status.get('load')}")
        print("-------------------------\n")
    else:
        print(f"[ERR] Could not fetch status for Servo {id}")


# === HIGH-LEVEL ROBOT FUNCTIONS ===

def torque_all(enable=True, servo_ids=[0, 1, 3, 4, 5, 7]):
    """Enable or disable torque for a list of arm servos."""
    for sid in servo_ids:
        set_torque(sid, enable)

def move_arm_raw(positions, speed=800, acc=50, servo_ids=[0, 1, 3, 4, 5, 7]):
    """
    Move multiple joints simultaneously using raw encoder positions.
    """
    torque_all(True, servo_ids)
    for sid, pos in zip(servo_ids, positions):
        move(sid, pos, speed, acc)


def calibrate_zero_position(id):
    """
    Saves the servo's CURRENT physical position as its new zero/middle position 
    permanently in its EEPROM.
    """
    try:
        url = f"{ESP_IP}/calibrate?id={id}"
        resp = requests.get(url, timeout=2.0)
        if resp.status_code == 200:
            print(f"[OK] Servo {id} zero position calibrated successfully!")
        else:
            print(f"[ERR] Calibration failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"[ERR] Connection issue during calibration: {e}")

if __name__ == "__main__":
    print(f"Connecting to ESP32 arm controller at {ESP_IP}...")
    id = 1
    # Check status of Servo 0
    print_servo_status(id)
    # calibrate_zero_position(id)

    # Move a single joint to raw position 2048 (~180 degrees)
    # set_torque(id, False)
    # move(id=id, pos=0, speed=800)

    # Move using degrees directly
    move_angle(id=id, angle_deg=0, speed=1000)

    # Control Gripper
    # set_gripper(90)
