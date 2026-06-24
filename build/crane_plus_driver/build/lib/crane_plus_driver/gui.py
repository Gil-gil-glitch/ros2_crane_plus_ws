import sys

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import JointState

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QSlider,
    QPushButton,
)
from PyQt5.QtCore import Qt


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

        self.setWindowTitle("Crane+ Control")

        self.layout = QVBoxLayout()

        self.joint_names = [
            "crane_plus_joint1",
            "crane_plus_joint2",
            "crane_plus_joint3",
            "crane_plus_joint4",
            "crane_plus_joint_hand",
        ]

        self.sliders = []

        for joint in self.joint_names:

            label = QLabel(joint)
            self.layout.addWidget(label)

            slider = QSlider(Qt.Horizontal)

            # -150 deg to +150 deg
            slider.setMinimum(-150)
            slider.setMaximum(150)
            slider.setValue(0)

            slider.valueChanged.connect(
                self.publish_positions
            )

            self.sliders.append(slider)
            self.layout.addWidget(slider)

        home_button = QPushButton("Home")

        home_button.clicked.connect(
            self.home_position
        )

        self.layout.addWidget(home_button)

        self.setLayout(self.layout)

    def home_position(self):

        for slider in self.sliders:
            slider.setValue(0)

        self.publish_positions()

    def publish_positions(self):

        msg = JointState()

        msg.name = self.joint_names

        msg.position = [
            slider.value() * 3.14159 / 180.0
            for slider in self.sliders
        ]

        self.ros_node.pub.publish(msg)


def main():

    rclpy.init()

    ros_node = RosPublisher()

    app = QApplication(sys.argv)

    gui = CraneGUI(ros_node)
    gui.show()

    from PyQt5.QtCore import QTimer

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