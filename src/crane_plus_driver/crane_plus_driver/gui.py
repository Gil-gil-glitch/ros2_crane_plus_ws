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

        self.pub = self.create_publisher(
            JointState,
            "/crane_plus_command",
            10
        )


class CraneGUI(QWidget):

    def __init__(self, ros_node):
        super().__init__()

        self.ros_node = ros_node

        self.setWindowTitle("Crane+ Slider Control")
        self.resize(900, 400)

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

        title = QLabel("Crane+ Manual Control")
        title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title)

        for joint_name in self.joint_names:

            row = QHBoxLayout()

            joint_label = QLabel(joint_name)
            joint_label.setMinimumWidth(180)

            slider = QSlider(Qt.Horizontal)

            # Degrees
            slider.setMinimum(-150)
            slider.setMaximum(150)
            slider.setValue(0)

            value_label = QLabel("0° (0.00 rad)")
            value_label.setMinimumWidth(120)

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
        home_button.clicked.connect(self.home_position)

        button_row.addWidget(home_button)

        self.layout.addLayout(button_row)

        self.setLayout(self.layout)

    def update_label(self, label, deg):

        rad = math.radians(deg)

        label.setText(
            f"{deg:>4d}° ({rad:+.2f} rad)"
        )

    def home_position(self):

        for slider in self.sliders:
            slider.setValue(0)

        self.publish_positions()

    def publish_positions(self):

        msg = JointState()

        msg.name = self.joint_names

        msg.position = [
            math.radians(slider.value())
            for slider in self.sliders
        ]

        self.ros_node.pub.publish(msg)


def main():

    rclpy.init()

    ros_node = RosPublisher()

    app = QApplication(sys.argv)

    gui = CraneGUI(ros_node)
    gui.show()

    timer = QTimer()

    timer.timeout.connect(
        lambda: rclpy.spin_once(
            ros_node,
            timeout_sec=0.0
        )
    )

    timer.start(10)

    app.exec()

    ros_node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()