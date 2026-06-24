# Crane+ Robot Arm Control Guide

## Overview

The Crane+ robot arm is a **4-DOF robotic manipulator** with an additional **1-DOF gripper**, giving a total of **5 controllable joints**.

| Joint | Description |
|---------|-------------|
| crane_plus_joint1 | Base rotation |
| crane_plus_joint2 | Shoulder |
| crane_plus_joint3 | Elbow |
| crane_plus_joint4 | Wrist |
| crane_plus_joint_hand | Gripper |

The arm is controlled through a custom ROS 2 driver using Dynamixel AX-12A servos.

---

# System Architecture

GUI → ROS2 Topic → Driver Node → Dynamixel SDK → AX-12A Motors

Topics:

### Joint Commands

```bash
/crane_plus_command
```

Message type:

```bash
sensor_msgs/msg/JointState
```

### Speed Commands

```bash
/crane_plus_speed
```

Message type:

```bash
std_msgs/msg/Int32
```

---

# Starting the Driver

Open a terminal:

```bash
source ~/ros2_crane_ws/install/setup.bash
```

Start the driver:

```bash
ros2 run crane_plus_driver driver_node
```

Expected output:

```text
Connected to Dynamixels on /dev/ttyACM1
```

---

# Starting the GUI

Open a second terminal:

```bash
source ~/ros2_crane_ws/install/setup.bash
```

Launch the GUI:

```bash
ros2 run crane_plus_driver gui_node
```

The control panel should appear with:

- Joint sliders
- Speed slider
- Home Position button
- Pick Can button
- Confirm Grip button
- Place Can button

---

# Moving a Single Joint from Terminal

Example:

Move Joint 1 (base) by 0.5 radians:

```bash
ros2 topic pub --once /crane_plus_command sensor_msgs/msg/JointState \
"{name:['crane_plus_joint1'], position:[0.5]}"
```

---

# Moving Multiple Joints from Terminal

Example:

```bash
ros2 topic pub --once /crane_plus_command sensor_msgs/msg/JointState \
"{name:[
'crane_plus_joint1',
'crane_plus_joint2',
'crane_plus_joint3',
'crane_plus_joint4'
],
position:[
0.0,
0.5,
-1.0,
0.7
]}"
```

---

# Opening and Closing the Gripper

Close gripper:

```bash
ros2 topic pub --once /crane_plus_command sensor_msgs/msg/JointState \
"{name:['crane_plus_joint_hand'], position:[-1.0]}"
```

Open gripper:

```bash
ros2 topic pub --once /crane_plus_command sensor_msgs/msg/JointState \
"{name:['crane_plus_joint_hand'], position:[0.5]}"
```

Note:

- Negative values close the gripper.
- Positive values open the gripper.
- Exact limits depend on the physical setup.

---

# Speed Control

The GUI contains a speed slider.

The speed value is sent to:

```bash
/crane_plus_speed
```

Example terminal command:

```bash
ros2 topic pub --once /crane_plus_speed std_msgs/msg/Int32 \
"{data:25}"
```

Meaning:

| Value | Speed |
|---------|--------|
| 10 | Very slow |
| 25 | Recommended |
| 50 | Medium |
| 100 | Maximum |

---

# Manual GUI Control

The GUI provides direct control over every joint.

## Joint Sliders

Each slider controls one servo:

- Joint 1 → Base rotation
- Joint 2 → Shoulder
- Joint 3 → Elbow
- Joint 4 → Wrist
- Joint Hand → Gripper

Current angle is displayed as:

```text
45° (0.79 rad)
```

Moving a slider immediately publishes a command to the robot.

---

# Home Position

Press:

```text
Home Position
```

The arm returns to:

```text
Joint1 = 0°
Joint2 = 0°
Joint3 = 0°
Joint4 = 0°
Gripper = 0°
```

This is useful before beginning demonstrations.

---

# Soda Can Pickup Demonstration

The GUI contains a semi-automatic pickup sequence intended for classroom demonstrations.

The sequence is broken into multiple stages so the user can adjust the grip manually.

---

## Step 1: Approach Can

Press:

```text
Pick Can
```

The arm moves to a predefined approach position.

Example pose:

```text
Joint1 = 0°
Joint2 = 35°
Joint3 = -85°
Joint4 = 55°
Gripper = partially closed
```

The robot stops and waits.

Status:

```text
Check grip then press Confirm Grip
```

---

## Step 2: Adjust Grip

At this stage the user may:

- Open the gripper slightly
- Close the gripper slightly
- Verify the can is secure

The gripper slider remains active.

This allows the operator to compensate for:

- Different can sizes
- Positioning errors
- Uneven grasping

---

## Step 3: Lift Can

Press:

```text
Confirm Grip
```

The robot:

1. Stores the current gripper position.
2. Lifts the can upward.
3. Maintains the grip angle chosen by the operator.

Status:

```text
Can lifted. Press Place Can.
```

---

## Step 4: Move to Drop-Off Location

Press:

```text
Place Can
```

The robot:

1. Rotates Joint 1.
2. Moves toward the placement position.
3. Preserves the selected grip force.

Example:

```text
Rotate 90°
Move above target
Lower arm
```

---

## Step 5: Release Can

The robot automatically:

1. Opens the gripper.
2. Releases the can.
3. Ends the sequence.

Status:

```text
Can placed successfully.
```

---

# Future Project Goal

The eventual competition goal is:

1. Detect a soda can using a camera.
2. Estimate the can position.
3. Move automatically to the can.
4. Grasp the can.
5. Transport the can to a designated location.

Current status:

- Manual joint control [COMPLETED]

- Manual gripper control [COMPLETED]

- Adjustable speed control [COMPLETED]

- Semi-automatic pickup sequence [COMPLETED]

- Vision-based can detection

- Automatic target localization

- Autonomous pick-and-place

---

# Useful ROS Commands

View joint commands:

```bash
ros2 topic echo /crane_plus_command
```

View speed commands:

```bash
ros2 topic echo /crane_plus_speed
```

List nodes:

```bash
ros2 node list
```

List topics:

```bash
ros2 topic list
```

Check connected Dynamixels:

```bash
python3 scan_IDs.py
```

Expected result:

```text
Found: 1
Found: 2
Found: 3
Found: 4
Found: 5
```

---

# Hardware

Robot Arm:

- RT Corporation Crane+
- 4 DOF arm

Servos:

- Dynamixel AX-12A
- Protocol 1.0
- 1 Mbps communication

Controller Interface:

- USB serial adapter
- Typical device:

```bash
/dev/ttyACM1
```

Baudrate:

```text
1000000
```

---

# Notes for Students

1. Always start with the speed slider set low.
2. Keep hands away from moving joints.
3. Use Home Position before testing.
4. Verify the gripper can securely hold the can before lifting.
5. Tune pickup poses as necessary for your specific setup.
6. Future improvements should focus on camera-based can detection and autonomous grasping.