#!/usr/bin/env python3 
import sys 
import math 
import rclpy 
from rclpy.node import Node 
from sensor_msgs.msg import JointState 
from std_msgs.msg import Int32 
from PyQt5.QtWidgets import ( QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton, ) 
from PyQt5.QtCore import Qt, QTimer

class RosPublisher(Node):

    def __init__(self):
        super().__init__("crane_plus_gui")

        self.joint_pub = self.create_publisher(
            JointState,
            "/crane_plus_command",
            10
        )

        self.speed_pub = self.create_publisher(
            Int32,
            "/crane_plus_speed",
            10
        )

class CraneGUI(QWidget):

    def __init__(self, ros_node):
        super().__init__()

        self.ros_node = ros_node

        self.setWindowTitle("Crane+ Control Panel")
        self.resize(1000, 600)

        self.pick_state = "idle"

        self.joint_names = [
            "crane_plus_joint1",
            "crane_plus_joint2",
            "crane_plus_joint3",
            "crane_plus_joint4",
            "crane_plus_joint_hand",
        ]

        self.sliders = []
        self.value_labels = []

        self.layout = QVBoxLayout()

        title = QLabel("Crane+ Robot Arm Control")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            "font-size: 20px; font-weight: bold;"
        )
        self.layout.addWidget(title)

        self.status_label = QLabel("Status: Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.status_label)

        #
        # SPEED SLIDER
        #
        speed_row = QHBoxLayout()

        speed_text = QLabel("Speed")
        speed_text.setMinimumWidth(180)

        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(100)
        self.speed_slider.setValue(25)

        self.speed_value_label = QLabel("25%")
        self.speed_value_label.setMinimumWidth(120)

        self.speed_slider.valueChanged.connect(
            self.update_speed
        )

        speed_row.addWidget(speed_text)
        speed_row.addWidget(self.speed_slider)
        speed_row.addWidget(self.speed_value_label)

        self.layout.addLayout(speed_row)

        #
        # JOINT SLIDERS
        #
        for joint_name in self.joint_names:

            row = QHBoxLayout()

            joint_label = QLabel(joint_name)
            joint_label.setMinimumWidth(180)

            slider = QSlider(Qt.Horizontal)

            slider.setMinimum(-150)
            slider.setMaximum(150)
            slider.setValue(0)

            value_label = QLabel("0° (0.00 rad)")
            value_label.setMinimumWidth(150)

            slider.valueChanged.connect(
                lambda value, lbl=value_label:
                self.update_joint_label(lbl, value)
            )

            slider.valueChanged.connect(
                self.publish_positions
            )

            self.sliders.append(slider)
            self.value_labels.append(value_label)

            row.addWidget(joint_label)
            row.addWidget(slider)
            row.addWidget(value_label)

            self.layout.addLayout(row)

        #
        # BUTTONS
        #
        button_row = QHBoxLayout()

        self.home_button = QPushButton("Home Position")
        self.home_button.clicked.connect(
            self.home_position
        )

        self.pick_button = QPushButton("Pick Can")
        self.pick_button.clicked.connect(
            self.pick_can
        )

        self.confirm_button = QPushButton("Confirm Grip")
        self.confirm_button.clicked.connect(
            self.confirm_grip
        )

        self.placeLeft_button = QPushButton("Place Can Left")
        self.placeLeft_button.clicked.connect(
            self.place_can_left
        )

        self.placeRight_button = QPushButton("Place Can Right")
        self.placeRight_button.clicked.connect(
            self.place_can_right
        )

        self.catapult_button = QPushButton("Catapult Can")
        self.catapult_button.clicked.connect(
            self.catapult_can
        )

        self.confirm_button.setEnabled(False)
        self.placeLeft_button.setEnabled(False)
        self.placeRight_button.setEnabled(False)
        self.catapult_button.setEnabled(False)

        button_row.addWidget(self.home_button)
        button_row.addWidget(self.pick_button)
        button_row.addWidget(self.confirm_button)
        button_row.addWidget(self.placeLeft_button)
        button_row.addWidget(self.placeRight_button)
        button_row.addWidget(self.catapult_button)

        self.layout.addLayout(button_row)

        self.setLayout(self.layout)

        self.update_speed(
            self.speed_slider.value()
        )

    def update_speed(self, value):

        self.speed_value_label.setText(
            f"{value}%"
        )

        msg = Int32()
        msg.data = value

        self.ros_node.speed_pub.publish(msg)

    def update_joint_label(self, label, deg):

        rad = math.radians(deg)

        label.setText(
            f"{deg:>4d}° ({rad:+.2f} rad)"
        )

    def publish_positions(self):

        msg = JointState()

        msg.name = self.joint_names

        msg.position = [
            math.radians(slider.value())
            for slider in self.sliders
        ]

        self.ros_node.joint_pub.publish(msg)

    def apply_pose(self, pose_deg):
        # Block signals to avoid redundant mid-loop publishes
        for slider, angle in zip(self.sliders, pose_deg):
            slider.blockSignals(True)
            slider.setValue(angle)
            slider.blockSignals(False)

        self.publish_positions() 

    def home_position(self):

        self.pick_state = "idle"

        self.confirm_button.setEnabled(False)
        self.placeLeft_button.setEnabled(False)
        self.placeRight_button.setEnabled(False)
        self.catapult_button.setEnabled(False)

        self.status_label.setText(
            "Status: Returning Home"
        )

        home_pose = [
            0,
            0,
            0,
            0,
            0
        ]

        self.apply_pose(home_pose)

    def pick_can(self):

        self.status_label.setText(
            "Approaching soda can..."
        )

        initialthingy_pose = {
            0,
            35,
            -100,
            0,
            -35
        }

        self.apply_pose(
            initialthingy_pose
        )
        #
        # Tune these values on the real robot
        # 15.5 cm
        
        approach_pose = [ 
            0,
            90,
            -100,
            70,
            -35
        ]

        QTimer.singleShot(
            2500,
            lambda:
            self.apply_pose(
                approach_pose
            )
        )

        approach_pose = [ 
            0,
            97,
            -60,
            70,
            -35
        ]
        """
        self.apply_pose(
            approach_pose
        )
        """

        QTimer.singleShot(
            2500,
            lambda:
            self.apply_pose(
                approach_pose
            )
        )

        self.pick_state = "approaching"

        self.confirm_button.setEnabled(True)

        self.status_label.setText(
            "Check grip then press Confirm Grip"
        )

    def confirm_grip(self):
        if self.pick_state != "approaching":
            return

        grip = self.sliders[4].value()

        lift_pose = [
            0,
            10,
            -45,
            20,
            grip
        ]

        self.apply_pose(lift_pose)

        self.pick_state = "grasped"          # ← this was missing
        self.placeLeft_button.setEnabled(True)
        self.placeRight_button.setEnabled(True)   
        self.catapult_button.setEnabled(True)
        self.status_label.setText(
            "Can lifted. Press Place Can."
        )

    def place_can_left(self):

        grip = self.sliders[4].value()

        if self.pick_state != "grasped":
            return

        self.status_label.setText(
            "Placing can..."
        )

        rotate_pose = [
            90,
            10,
            -45,
            20,
            grip
        ]

        place_pose = [
            90,
            95,
            -40,
            50,
            grip
        ]

        release_pose = [
            90,
            95,
            -45,
            50,
            -25
        ]

        self.apply_pose(
            rotate_pose
        )

        QTimer.singleShot(
            1500,
            lambda:
            self.apply_pose(
                place_pose
            )
        )

        QTimer.singleShot(
            3000,
            lambda:
            self.apply_pose(
                release_pose
            )
        )

        QTimer.singleShot(
            3500,
            self.finish_place
        )
    
    def catapult_can(self):
        grip = self.sliders[4].value()

        self.status_label.setText("Catapulting can...")

        approach_pose = [
            0,
            90,
            -60,
            70,
            grip
        ]

        throw_pose = [
            0,
            5,
            -5,
            5,
            grip
        ]

        thrown_pose = [
            0,
            -20,
            20,
            -20,
            grip - 25
        ]

        self.apply_pose(approach_pose)

        QTimer.singleShot(
            2000,
            lambda: self.apply_pose(throw_pose)
        )

        QTimer.singleShot(
            2150,
            lambda: self.apply_pose(thrown_pose)
        )

        QTimer.singleShot(
            2600,
            self.finish_place
        )

    def place_can_right(self):

        grip = self.sliders[4].value()

        if self.pick_state != "grasped":
            return

        self.status_label.setText(
            "Placing can..."
        )

        rotate_pose = [
            -90,
            10,
            -45,
            20,
            grip
        ]

        place_pose = [
            -90,
            95,
            -40,
            50,
            grip
        ]

        release_pose = [
            -90,
            95,
            -45,
            50,
            -25
        ]

        self.apply_pose(
            rotate_pose
        )

        QTimer.singleShot(
            1500,
            lambda:
            self.apply_pose(
                place_pose
            )
        )

        QTimer.singleShot(
            3000,
            lambda:
            self.apply_pose(
                release_pose
            )
        )

        QTimer.singleShot(
            3500,
            self.finish_place
        )

    def finish_place(self):

        self.pick_state = "idle"

        self.confirm_button.setEnabled(False)
        self.placeLeft_button.setEnabled(False)
        self.placeRight_button.setEnabled(False) 
        self.catapult_button.setEnabled(False)

        self.status_label.setText(
            "Can placed successfully."
        )

def main():

    rclpy.init()

    ros_node = RosPublisher()

    app = QApplication(sys.argv)

    gui = CraneGUI(ros_node)

    gui.show()

    ros_timer = QTimer()

    ros_timer.timeout.connect(
        lambda:
        rclpy.spin_once(
            ros_node,
            timeout_sec=0.0
        )
    )

    ros_timer.start(10)

    app.exec()

    ros_node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
