"""
Parametric Chain (TEMPLATE)

Fill in the TODO sections below. Refer to:
  - Guide Section 3: Kinematics Fundamentals (what FK/IK actually compute)
  - Guide Section 5: Walkthrough - Solving IK with inverse_kinematics.py

Do NOT run this against the physical arm until your simulation (the
matplotlib plot at the bottom) shows a sensible pose and the printed
distance error is small. Dry-run first - always.
"""

import ikpy.chain
import numpy as np
import matplotlib.pyplot as plt

# CONFIGURATION & FACTORY FUNCTIONS

def get_default_arm_params():
    """Returns default lengths and joint limits for easy reconfiguration."""
    return {
        # Link Lengths (mm) - from the SO-101 spec (Guide Section 5.1)
        "L1": 85.0,
        "L2": 127.0,
        "L3": 110.0,
        "L4": 65.0,
        "L5": 35.0,
        "L6": 135.0,

        # Joint Limits (Degrees)
        "limits": {
            "base_pan": (-290, 290),
            "shoulder_pitch": (15, 165),
            "elbow_pitch": (9.5, 174),
            "wrist_pitch": (3, 174),
            "wrist_twist": (-70, 70)
        }
    }

def create_arm_chain(params=None):
    """
    Builds and returns an ikpy Chain object based on provided link lengths and limits.
    """
    if params is None:
        params = get_default_arm_params()

    L1, L2, L3, L4, L5, L6 = params["L1"], params["L2"], params["L3"], params["L4"], params["L5"], params["L6"]
    lim = params["limits"]

    # Convert limits to radians
    bounds = {key: (np.deg2rad(val[0]), np.deg2rad(val[1])) for key, val in lim.items()}

    chain = ikpy.chain.Chain(name='configurable_arm', links=[
        ikpy.link.URDFLink(
            name="world_fixed",
            origin_translation=[0, 0, 0],
            origin_orientation=[0, 0, 0],
            rotation=[0, 0, 0],
        ),
        ikpy.link.URDFLink(
            name='base_pan_joint',
            origin_translation=[0, 0, 0],
            origin_orientation=[0, 0, 0],
            rotation=[0, 0, 1],
            bounds=bounds["base_pan"],
        ),
        ikpy.link.URDFLink(
            name='shoulder_pitch_joint',
            origin_translation=[0, 0, L1],
            origin_orientation=[0, 0, 0],
            rotation=[0, -1, 0],
            bounds=bounds["shoulder_pitch"],
        ),
        ikpy.link.URDFLink(
            name='elbow_pitch_joint',
            origin_translation=[L2, 0, 0],
            origin_orientation=[0, (np.pi/2), 0],
            rotation=[0, -1, 0],
            bounds=bounds["elbow_pitch"],
        ),
        ikpy.link.URDFLink(
            name='wrist_pitch_joint',
            origin_translation=[L3, 0, 0],
            origin_orientation=[0, (np.pi/2), 0],
            rotation=[0, -1, 0],
            bounds=bounds["wrist_pitch"],
        ),
        ikpy.link.URDFLink(
            name='wrist_pitch_offset',
            origin_translation=[L4, 0, 0],
            origin_orientation=[0, 0, 0],
            rotation=[0, 0, 0],
        ),
        ikpy.link.URDFLink(
            name='wrist_twist_joint',
            origin_translation=[0, 0, L5],
            origin_orientation=[0, 0, 0],
            rotation=[1, 0, 0],
        ),
        ikpy.link.URDFLink(
            name='gripper_end_joint',
            origin_translation=[L6, 0, 0],
            origin_orientation=[0, 0, 0],
            rotation=[0, 0, 0],
        )
    ],
    # TODO (Guide Section 5.2 "The Active Links Mask"):
    # There are 8 links defined above, in this order:
    #   0 world_fixed        (never moves)
    #   1 base_pan_joint      <- a real motor
    #   2 shoulder_pitch_joint<- a real motor
    #   3 elbow_pitch_joint   <- a real motor
    #   4 wrist_pitch_joint   <- a real motor
    #   5 wrist_pitch_offset  (fixed spacer, no motor)
    #   6 wrist_twist_joint   <- a real motor (not needed for XYZ-only targeting)
    #   7 gripper_end_joint   (fixed, the gripper tip)
    #
    # Build an 8-item list of True/False: True where the optimizer is allowed
    # to move that joint, False where it must stay fixed. For plain [X, Y, Z]
    # position targeting you only need the first 4 real joints active.
    active_links_mask=[False, ?, ?, ?, ?, ?, ?, ?]  #fill in the rest
    )
    return chain


# KINEMATICS SOLVER and VERIFIER
#Task 1b:Implement Ik SOLVE

def calculate_joint_angles(chain, target_position, initial_joint_angles=[0, 0, 30, 30, 30, 0, 0, 0], max_iter=100):
    """
    Computes inverse kinematics for a target 3D position [x, y, z].
    Returns: (joint_angles_degrees, joint_angles_radians, specific_arm_angles)
    """
    initial_position_rad = np.deg2rad(initial_joint_angles)

    # TODO (Guide Section 3 "How IKPy Solves the Problem"):
    # Call chain.inverse_kinematics(...) to solve for the joint angles that
    # place the end effector at `target_position`. You'll need to pass:
    #   - the target position
    #   - initial_position=initial_position_rad  (the starting guess)
    #   - max_iter=max_iter
    # Store the result (in radians) in `joint_angles_rad`.
    joint_angles_rad = None  # <-- replace with your chain.inverse_kinematics(...) call


    joint_angles_deg = np.rad2deg(joint_angles_rad)

    # Extract specific physical servo indices
    arm_servo_angles = [
        joint_angles_deg[1],  # Base Pan
        joint_angles_deg[2],  # Shoulder Pitch
        joint_angles_deg[3],  # Elbow Pitch
        joint_angles_deg[4],  # Wrist Pitch
        joint_angles_deg[6]   # Wrist Twist
    ]

    print(f"Calculated Joint Angles (degrees):")
    print(f"  Joint 1 (Base):         {joint_angles_deg[1]:.2f}")
    print(f"  Joint 2 (Shoulder):     {joint_angles_deg[2]:.2f}")
    print(f"  Joint 3 (Elbow):        {joint_angles_deg[3]:.2f}")
    print(f"  Joint 4 (Wrist Pitch):  {joint_angles_deg[4]:.2f}")
    print(f"  Joint 5 (Wrist Twist):  {joint_angles_deg[6]:.2f}")

    return joint_angles_deg, joint_angles_rad, arm_servo_angles

def verify_kinematics(chain, joint_angles_deg, target_position, tolerance=2.0):
    """
    Runs forward kinematics on calculated angles to verify distance error from target.
    """
    joint_angles_rad = np.deg2rad(joint_angles_deg)

    # TODO (Guide Section 3 "Forward vs. Inverse Kinematics"):
    # Run forward kinematics on joint_angles_rad to get the resulting 4x4
    # transform matrix, then pull the [x, y, z] position out of it.
    # Hint: chain.forward_kinematics(joint_angles_rad) returns a 4x4 matrix;
    # the position is the top-right 3x1 column, i.e. matrix[:3, 3].
    real_position_matrix = None  # <-- replace with your chain.forward_kinematics(...) call
    real_position = None         # <-- extract [x, y, z] from real_position_matrix

    distance_error = np.linalg.norm(np.array(target_position) - real_position)

    print(f"Target Position: {target_position}")
    print(f"Achieved Position: {real_position}")
    print(f"Distance error from target: {distance_error:.4f} mm")

    if distance_error > tolerance:
        print("[WARN] IK solution exceeds error tolerance.")
        return False
    else:
        print("[OK] IK solution verified successfully!")
        return True


# VISUALIZATION TOOLS

class ArmVisualizer:
    """Manages 3D Matplotlib visualization cleanly without global variable clutter."""
    def __init__(self, chain, workspace_limit=450):
        self.chain = chain
        self.workspace_limit = workspace_limit

        plt.ion()
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')

    def plot_static(self, joint_angles_deg, target_position=None):
        plt.ioff()
        joint_angles_rad = np.deg2rad(joint_angles_deg)
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        self.chain.plot(joint_angles_rad, ax, target=target_position)
        self._configure_axis(ax)
        plt.show()

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


# MAIN EXECUTION FLOW

if __name__ == '__main__':
    # 1. Initialize Arm Chain & Visualizer
    arm_params = get_default_arm_params()
    my_arm_chain = create_arm_chain(arm_params)
    visualizer = ArmVisualizer(my_arm_chain, workspace_limit=450)

    # TODO: Pick your own target [X, Y, Z] in mm, within ~400mm of the base.
    target = [100.0, 150.0, 310.0]
    initial_guess = [0, 0, 30, 30, 30, 0, 0, 0]

    # 3. Calculate IK
    angles_deg, angles_rad, servo_subset = calculate_joint_angles(
        chain=my_arm_chain,
        target_position=target,
        initial_joint_angles=initial_guess
    )

    # 4. Verify Accuracy
    verify_kinematics(my_arm_chain, angles_deg, target)

    # 5. Render in 3D
    visualizer.update_plot(angles_deg, target_position=target)

    # Keep plot open if run as main script
    plt.ioff()
    plt.show()
