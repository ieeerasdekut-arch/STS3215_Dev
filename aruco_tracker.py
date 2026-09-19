import cv2
import cv2.aruco as aruco
import numpy as np

# ==========================================
# === CONFIGURATION                        ===
# ==========================================
ARUCO_DICT = aruco.DICT_4X4_50

BASE_MARKER_ID = 0      # Marker placed at the robot base origin
OBJECT1_MARKER_ID = 1
OBJECT2_MARKER_ID = 3    # Marker placed on target object 2

MARKER_SIZE_METERS = 0.042  # 4.2 cm

# Camera Calibration Parameters
CAMERA_MATRIX = np.array([
    [800.0, 0.0, 320.0],  # [fx, 0, cx]
    [0.0, 800.0, 240.0],  # [0, fy, cy]
    [0.0,   0.0,   1.0]
], dtype=np.float32)

DIST_COEFFS = np.zeros((5, 1), dtype=np.float32)


class ArUcoLocalization:
    def __init__(self, marker_size, camera_matrix, dist_coeffs, aruco_dict_type):
        self.marker_size = marker_size
        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs
        
        self.aruco_dict = aruco.getPredefinedDictionary(aruco_dict_type)
        self.aruco_params = aruco.DetectorParameters()
        self.detector = aruco.ArucoDetector(self.aruco_dict, self.aruco_params)

        half_size = marker_size / 2.0
        self.obj_points = np.array([
            [-half_size,  half_size, 0.0],  # Top-left
            [ half_size,  half_size, 0.0],  # Top-right
            [ half_size, -half_size, 0.0],  # Bottom-right
            [-half_size, -half_size, 0.0]   # Bottom-left
        ], dtype=np.float32)

    def process_frame(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = self.detector.detectMarkers(gray)

        base_pose = None
        object1_pose = None
        object2_pose = None
        object1_relative_to_base = None
        object2_relative_to_base = None

        if ids is not None and len(ids) > 0:
            aruco.drawDetectedMarkers(frame, corners, ids)

            poses = {}
            for i, marker_id in enumerate(ids.flatten()):
                marker_corners = corners[i][0]

                success, rvec, tvec = cv2.solvePnP(
                    self.obj_points, 
                    marker_corners, 
                    self.camera_matrix, 
                    self.dist_coeffs, 
                    flags=cv2.SOLVEPNP_ITERATIVE
                )

                if success:
                    cv2.drawFrameAxes(frame, self.camera_matrix, self.dist_coeffs, rvec, tvec, self.marker_size * 0.5)
                    poses[marker_id] = {"rvec": rvec, "tvec": tvec}

            # 1. Check if Base Marker is visible
            if BASE_MARKER_ID in poses:
                base_pose = (poses[BASE_MARKER_ID]["tvec"], poses[BASE_MARKER_ID]["rvec"])

            # 2. Check if Object Markers are visible & compute relative to base independently
            if base_pose:
                if OBJECT1_MARKER_ID in poses:
                    object1_pose = (poses[OBJECT1_MARKER_ID]["tvec"], poses[OBJECT1_MARKER_ID]["rvec"])
                    object1_relative_to_base = self.transform_to_base_frame(
                        poses[BASE_MARKER_ID], poses[OBJECT1_MARKER_ID]
                    )

                if OBJECT2_MARKER_ID in poses:
                    object2_pose = (poses[OBJECT2_MARKER_ID]["tvec"], poses[OBJECT2_MARKER_ID]["rvec"])
                    object2_relative_to_base = self.transform_to_base_frame(
                        poses[BASE_MARKER_ID], poses[OBJECT2_MARKER_ID]
                    )

        return frame, base_pose, object1_pose, object1_relative_to_base, object2_pose, object2_relative_to_base

    def transform_to_base_frame(self, base_pose, obj_pose):
        """
        Transforms a single object's 3D position from the Camera coordinate frame 
        into the Robot Base coordinate frame.
        """
        R_cam_base, _ = cv2.Rodrigues(base_pose["rvec"])
        T_cam_base = base_pose["tvec"]

        R_cam_obj, _ = cv2.Rodrigues(obj_pose["rvec"])
        T_cam_obj = obj_pose["tvec"]

        # Invert camera-to-base transformation to get base-to-camera matrix
        T_cam_to_base_rot = R_cam_base.T
        T_cam_to_base_trans = -T_cam_to_base_rot @ T_cam_base

        # Calculate object position relative to the base frame
        obj_pos_in_base = T_cam_to_base_rot @ T_cam_obj + T_cam_to_base_trans
        
        # Convert to a 1D standard numpy array and convert from meters to millimeters
        obj_pos_mm = obj_pos_in_base.flatten() * 1000.0
        
        return obj_pos_mm


def get_object_positions(cap):
      
    tracker = ArUcoLocalization(
        marker_size=MARKER_SIZE_METERS,
        camera_matrix=CAMERA_MATRIX,
        dist_coeffs=DIST_COEFFS,
        aruco_dict_type=ARUCO_DICT
    )

    ret, frame = cap.read()
    if not ret:
        print("[ERR] Failed to grab frame.")
        # while True:
        #     time.sleep(1)
        #     print("[ERR] Waiting for camera to be available...")

    processed_frame, base, object1_pose, object1_relative_to_base, object2_pose, object2_relative_to_base = tracker.process_frame(frame)

    if base is not None:
        cv2.putText(processed_frame, "Base Marker Found", (30, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
    if object1_relative_to_base is not None:
        text = f"Object 1 (Base-Rel) X:{object1_relative_to_base[0]:.1f} Y:{object1_relative_to_base[1]:.1f} Z:{object1_relative_to_base[2]:.1f} mm"
        cv2.putText(processed_frame, text, (30, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        object1_pos = [object1_relative_to_base[0], object1_relative_to_base[1]]

    if object2_relative_to_base is not None:
        text = f"Object 2 (Base-Rel) X:{object2_relative_to_base[0]:.1f} Y:{object2_relative_to_base[1]:.1f} Z:{object2_relative_to_base[2]:.1f} mm"
        cv2.putText(processed_frame, text, (30, 110), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        object2_pos = [object2_relative_to_base[0], object2_relative_to_base[1]]

    if object1_relative_to_base is not None and object2_relative_to_base is not None:
        return object1_pos, object2_pos
    else:
        print("[WARN] Could not determine object positions. Returning None.")
        return None, None


# ==========================================
# === MAIN EXECUTION LOOP                  ===
# ==========================================

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("[ERR] Could not open video stream.")
        exit()

    tracker = ArUcoLocalization(
        marker_size=MARKER_SIZE_METERS,
        camera_matrix=CAMERA_MATRIX,
        dist_coeffs=DIST_COEFFS,
        aruco_dict_type=ARUCO_DICT
    )

    print("[INFO] Starting ArUco Tracker. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERR] Failed to grab frame.")
            break

        processed_frame, base, object1_pose, object1_relative_to_base, object2_pose, object2_relative_to_base = tracker.process_frame(frame)

        if base is not None:
            cv2.putText(processed_frame, "Base Marker Found", (30, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
        if object1_relative_to_base is not None:
            text = f"Object 1 (Base-Rel) X:{object1_relative_to_base[0]:.1f} Y:{object1_relative_to_base[1]:.1f} Z:{object1_relative_to_base[2]:.1f} mm"
            cv2.putText(processed_frame, text, (30, 70), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            object1_pos = [object1_relative_to_base[0], object1_relative_to_base[1]]

        if object2_relative_to_base is not None:
            text = f"Object 2 (Base-Rel) X:{object2_relative_to_base[0]:.1f} Y:{object2_relative_to_base[1]:.1f} Z:{object2_relative_to_base[2]:.1f} mm"
            cv2.putText(processed_frame, text, (30, 110), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            object2_pos = [object2_relative_to_base[0], object2_relative_to_base[1]]

        cv2.imshow("Robot ArUco Localization", processed_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()