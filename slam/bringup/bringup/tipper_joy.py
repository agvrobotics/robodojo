#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from std_msgs.msg import String

class TipperJoy(Node):
    def __init__(self):
        super().__init__('tipper_joy')
        self.pub = self.create_publisher(String, '/tipper_cmd', 10)
        self.sub = self.create_subscription(Joy, '/joy', self.joy_callback, 10)

        self.btn_Y = 3  # Y 
        self.btn_A = 0  # A 

        # Track last state to avoid spamming
        self.last_Y = 0
        self.last_A = 0

        self.get_logger().info("Tipper joystick control ready")

    def joy_callback(self, msg: Joy):
        y_pressed = msg.buttons[self.btn_Y]
        a_pressed = msg.buttons[self.btn_A]

        if y_pressed and not self.last_Y:
            self.pub.publish(String(data="1"))
        if a_pressed and not self.last_A:
            self.pub.publish(String(data="0"))

        self.last_Y = y_pressed
        self.last_A = a_pressed


def main(args=None):
    rclpy.init(args=args)
    node = TipperJoy()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
