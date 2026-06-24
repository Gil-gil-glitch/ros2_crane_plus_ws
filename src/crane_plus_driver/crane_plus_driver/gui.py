#!/usr/bin/env python3

import sys
import math

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import JointState
from std_msgs.msg import Int32

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSlider,
    QPushButton,
)

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

        home_button = QPushButton("Home Position")
        home_button.clicked.connect(
            self.home_position
        )

        pick_button = QPushButton("Pick Can")
        pick_button.clicked.connect(
            self.pick_sequence
        )

        button_row.addWidget(home_button)
        button_row.addWidget(pick_button)

        self.layout.addLayout(button_row)

        self.setLayout(self.layout)

        #
        # Publish initial speed
        #
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

        for slider, angle in zip(
            self.sliders,
            pose_deg
        ):
            slider.setValue(angle)

        self.publish_positions()

    def home_position(self):

        self.status_label.setText(
            "Status: Moving Home"
        )

        home_pose = [
            0,
            0,
            0,
            0,
            0
        ]

        self.apply_pose(home_pose)

    def pick_sequence(self):

        self.status_label.setText(
            "Status: Picking Soda Can"
        )

        #
        # Adjust after testing
        #
        approach_pose = [
            0,
            35,
            -85,
            55,
            25
        ]

        grasp_pose = [
            0,
            35,
            -85,
            55,
            -15
        ]

        self.apply_pose(
            approach_pose
        )

        QTimer.singleShot(
            1000,
            lambda:
            self.apply_pose(
                grasp_pose
            )
        )

        QTimer.singleShot(
            1500,
            lambda:
            self.status_label.setText(
                "Status: Pick Complete"
            )
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