import math

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import JointState

from dynamixel_sdk import PortHandler
from dynamixel_sdk import PacketHandler


PROTOCOL_VERSION = 1.0

PORT_NAME = "/dev/ttyACM1"
BAUDRATE = 1000000

ADDR_GOAL_POSITION = 30

JOINT_TO_ID = {
    "crane_plus_joint1": 1,
    "crane_plus_joint2": 2,
    "crane_plus_joint3": 3,
    "crane_plus_joint4": 4,
    "crane_plus_joint_hand": 5,
}


def rad_to_dxl(rad):
    deg = math.degrees(rad)

    value = int(
        ((deg + 150.0) / 300.0) * 1023.0
    )

    return max(0, min(1023, value))


class CranePlusDriver(Node):

    def __init__(self):
        super().__init__("crane_plus_driver")

        self.port_handler = PortHandler(PORT_NAME)
        self.packet_handler = PacketHandler(PROTOCOL_VERSION)

        if not self.port_handler.openPort():
            raise RuntimeError(f"Failed to open {PORT_NAME}")

        if not self.port_handler.setBaudRate(BAUDRATE):
            raise RuntimeError("Failed to set baudrate")

        self.get_logger().info(
            f"Connected to Dynamixels on {PORT_NAME}"
        )

        self.subscription = self.create_subscription(
            JointState,
            "/crane_plus_command",
            self.command_callback,
            10,
        )

    def command_callback(self, msg):

        for joint_name, position_rad in zip(
            msg.name,
            msg.position,
        ):

            if joint_name not in JOINT_TO_ID:
                self.get_logger().warn(
                    f"Unknown joint: {joint_name}"
                )
                continue

            dxl_id = JOINT_TO_ID[joint_name]

            goal_position = rad_to_dxl(position_rad)

            self.packet_handler.write2ByteTxRx(
                self.port_handler,
                dxl_id,
                ADDR_GOAL_POSITION,
                goal_position,
            )

            self.get_logger().info(
                f"{joint_name} -> {position_rad:.2f} rad "
                f"({goal_position})"
            )


def main(args=None):

    rclpy.init(args=args)

    node = CranePlusDriver()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()