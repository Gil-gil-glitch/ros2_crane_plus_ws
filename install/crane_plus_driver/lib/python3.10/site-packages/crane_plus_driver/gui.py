#!/usr/bin/env python3

import sys
import math

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import JointState

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

        self.publisher = self.create_publisher(
            JointState,
            "/crane_plus_command",
            10
        )


class CraneGUI(QWidget):

    def __init__(self, ros_node):
        super().__init__()

        self.ros_node = ros_node

        self.setWindowTitle("Crane+ Control Panel")
        self.resize(1000, 500)

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

        for joint_name in self.joint_names:

            row = QHBoxLayout()

            joint_label = QLabel(joint_name)
            joint_label.setMinimumWidth(180)

            slider = QSlider(Qt.Horizontal)

            slider.setMinimum(-150)
            slider.setMaximum(150)
            slider.setValue(0)

            value_label = QLabel("0° (0.00 rad)")
            value_label.setMinimumWidth(140)

            slider.valueChanged.connect(
                lambda value, lbl=value_label:
                self.update_label(lbl, value)
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

    def update_label(self, label, deg):

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

        self.ros_node.publisher.publish(msg)

    def apply_pose(self, pose_deg):

        for slider, angle in zip(
            self.sliders,
            pose_deg
        ):
            slider.setValue(angle)

        self.publish_positions()

    def home_position(self):

        self.status_label.setText(
            "Status: Moving to Home Position"
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
            "Status: Executing Pick Sequence"
        )

        #
        # CHANGE THESE VALUES AFTER TESTING
        #

        approach_pose = [
            0,      # base
            35,     # shoulder
            -85,    # elbow
            55,     # wrist
            25      # gripper open
        ]

        grasp_pose = [
            0,
            35,
            -85,
            55,
            -15     # gripper closed
        ]

        self.apply_pose(approach_pose)

        QTimer.singleShot(
            1000,
            lambda: self.apply_pose(grasp_pose)
        )

        QTimer.singleShot(
            1200,
            lambda: self.status_label.setText(
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
        lambda: rclpy.spin_once(
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