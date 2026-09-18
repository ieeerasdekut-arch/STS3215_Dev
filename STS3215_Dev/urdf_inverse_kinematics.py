"""
URDF-Based Chain (TEMPLATE)

Fill in the TODO sections below. Refer to:
  - Guide Section 6: Walkthrough - Solving IK with URDF (urdf_inverse_kinematics.py)
  - Guide Section 6 "URDF Joint to Physical Actuator Mapping" table

IMPORTANT UNITS NOTE: a URDF-loaded chain uses METERS, not millimeters,
unlike the hand-built chain in inverse_kinematics.py. A target of
[0.10, 0.15, 0.31] means 10cm / 15cm / 31cm - don't accidentally type
[100, 150, 310] here, that asks the arm to reach 100 meters away.

Do NOT run this against the physical arm until your simulation (the
matplotlib plot at the bottom) shows a sensible pose and the printed
distance error is small. Dry-run first - always.
"""

import ikpy.chain
import numpy as np
import matplotlib.pyplot as plt
import os

#URDF CHAIN LOADER

def load_arm_from_urdf(urdf_path, active_links_mask=None):
    """
    Loads an arm chain from a URDF file.

    :param urdf_path: Path to the .urdf file
    :param active_links_mask: Boolean list specifying which joints are active/movable
                              (e.g., [False, True, True, True, True, False])
    """
    if not os.path.exists(urdf_path):
        raise FileNotFoundError(f"Could not find URDF file at: {urdf_path}")

    # Load chain from URDF
    # active_links_mask defaults to all movable if not specified - but for this
    # URDF that's actually wrong, see the TODO in the __main__ block below for why.
    chain = ikpy.chain.Chain.from_urdf_file(
        urdf_path,
        active_links_mask=active_links_mask
    )

    return chain


#KINEMATICS SOLVER & VERIFIER

def calculate_joint_angles(chain, target_position, initial_joint_angles=None, max_iter=100):
    """
    Computes inverse kinematics for a target 3D position [x, y, z] using a URDF-based chain.
    """
    # If initial guess isn't provided, default to zeros matching the chain length
    if initial_joint_angles is None:
        initial_joint_angles = [0.0] * len(chain.links)

    initial_position_rad = np.deg2rad(initial_joint_angles)

    # TODO (same concept as inverse_kinematics.py, Guide Section 3):
    # Call chain.inverse_kinematics(...) with target_position, the initial
    # guess, and max_iter. Store the radian result in joint_angles_rad.
    joint_angles_rad = None  # <-- replace with your chain.inverse_kinematics(...) call

    joint_angles_deg = np.rad2deg(joint_angles_rad)

    print(f"Calculated Joint Angles (degrees) from URDF:")
    for idx, link in enumerate(chain.links):
        # Only print active joints or all depending on preference
        if chain.active_links_mask[idx]:
            print(f"  {link.name}: {joint_angles_deg[idx]:.2f}°")

    return joint_angles_deg, joint_angles_rad

def verify_kinematics(chain, joint_angles_deg, target_position, tolerance=2.0):
    """
    Runs forward kinematics on the calculated angles to verify distance error from target.
    """
    joint_angles_rad = np.deg2rad(joint_angles_deg)

    # TODO: same as inverse_kinematics.py's verify_kinematics() - run FK,
    # pull out [x, y, z], and compare it to target_position.
    real_position_matrix = None  # <-- chain.forward_kinematics(joint_angles_rad)
    real_position = None         # <-- real_position_matrix[:3, 3]

    distance_error = np.linalg.norm(np.array(target_position) - real_position)

    print(f"Target Position:   {target_position}")
    print(f"Achieved Position: {real_position.tolist()}")
    print(f"Distance error:    {distance_error:.4f} mm")

    if distance_error > tolerance:
        print("[WARN] IK solution exceeds error tolerance.")
        return False
    else:
        print("[OK] IK solution verified successfully!")
        return True


# ==========================================
# === VISUALIZATION TOOLS                  ===
# ==========================================

class ArmVisualizer:
    """Manages 3D Matplotlib visualization for URDF chains."""
    def __init__(self, chain, workspace_limit=450):
        self.chain = chain
        self.workspace_limit = workspace_limit

        plt.ion()
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')

    def update_plot(self, joint_angles_deg, target_position=None):
        """Updates the live interactive 3D plot."""
        joint_angles_rad = np.deg2rad(joint_angles_deg)
        self.ax.cla()

        self.chain.plot(joint_angles_rad, self.ax, target=target_position)
        self._configure_axis(self.ax)

        plt.draw()
        plt.pause(0.01)

    def _configure_axis(self, ax):
        ax.set_xlabel("X (mm)")
        ax.set_ylabel("Y (mm)")
        ax.set_zlabel("Z (mm)")
        ax.set_xlim(-self.workspace_limit, self.workspace_limit)
        ax.set_ylim(-self.workspace_limit, self.workspace_limit)
        ax.set_zlim(0, self.workspace_limit)


# ==========================================
# === MAIN EXECUTION FLOW                  ===
# ==========================================

if __name__ == '__main__':
    # 1. Path to your URDF file
    urdf_filename = "so101_new_calib.urdf"

    # TODO (Guide Section 6 "URDF Joint to Physical Actuator Mapping" table):
    # The URDF has 7 links in this order:
    #   0 Base link          (fixed)
    #   1 shoulder_pan        <- Motor 1
    #   2 shoulder_lift       <- Motor 2
    #   3 elbow_flex          <- Motor 3
    #   4 wrist_flex          <- Motor 4
    #   5 wrist_roll          <- Motor 5
    #   6 gripper_frame_joint (fixed - it's a mounting frame, not a moving joint)
    #
    # Build a 7-item True/False list. Get this wrong (e.g. leave it as None
    # so ikpy defaults to "everything active") and every motor ends up being
    # commanded with a DIFFERENT joint's angle than the one it's supposed to
    # move - a subtle, dangerous bug that produces plausible-looking numbers
    # that are actually wrong. Think carefully about which links are real,
    # moving motors vs. fixed geometry.
    custom_active_mask = None  # <-- replace with your 7-item list

    try:
        # Load Chain from URDF
        my_arm_chain = load_arm_from_urdf(urdf_filename, active_links_mask=custom_active_mask)

        # Initialize Visualizer
        visualizer = ArmVisualizer(my_arm_chain, workspace_limit=450)

        # TODO: Target coordinates (X, Y, Z) in METERS (see units note at top
        # of this file). Pick a point within ~0.4m of the base.
        target = [0.10, 0.15, 0.31]

        # Calculate IK
        angles_deg, angles_rad = calculate_joint_angles(
            chain=my_arm_chain,
            target_position=target
        )

        # Verify Accuracy via Forward Kinematics
        verify_kinematics(my_arm_chain, angles_deg, target)

        # Render the arm in 3D
        visualizer.update_plot(angles_deg, target_position=target)

        # Keep plot open
        plt.ioff()
        plt.show()

    except Exception as e:
        print(f"[ERR] Failed to execute URDF Inverse Kinematics: {e}")
