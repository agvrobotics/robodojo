import math
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan


class SlipDetector(Node):
    def __init__(self):
        super().__init__('slip_detector')

        # ---- Parameters ----
        self.declare_parameter('range_angle_deg', 0.0)     # angle to check (front)
        self.declare_parameter('distance_thresh', 0.15)    # meters difference to trigger
        self.declare_parameter('odom_thresh', 0.05)        # minimum odom move to evaluate

        self.angle_deg = self.get_parameter('range_angle_deg').value
        self.dist_thresh = self.get_parameter('distance_thresh').value
        self.odom_thresh = self.get_parameter('odom_thresh').value

        # ---- State ----
        self.last_odom_x = None
        self.last_odom_y = None
        self.last_scan_range = None

        # ---- Subscribers ----
        self.create_subscription(Odometry, 'odom', self.odom_cb, 10)
        self.create_subscription(LaserScan, 'scan', self.scan_cb, 10)

        self.get_logger().info("SlipDetector ready (listening to /odom and /scan)")

    # --- Helpers ---
    def odom_cb(self, msg: Odometry):
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        if self.last_odom_x is None:
            self.last_odom_x = x
            self.last_odom_y = y
            return

        # distance moved from last check
        self.odom_move = math.hypot(x - self.last_odom_x, y - self.last_odom_y)

    def scan_cb(self, msg: LaserScan):
        # Compute the index for the desired angle
        angle_rad = math.radians(self.angle_deg)
        idx = int((angle_rad - msg.angle_min) / msg.angle_increment)
        if idx < 0 or idx >= len(msg.ranges):
            return  # angle out of scan range

        range_val = msg.ranges[idx]

        if self.last_scan_range is None or self.last_odom_x is None:
            self.last_scan_range = range_val
            return

        # Only check when odom reports significant movement
        if self.odom_move >= self.odom_thresh:
            lidar_change = abs(range_val - self.last_scan_range)
            if abs(lidar_change - self.odom_move) > self.dist_thresh:
                self.get_logger().warn("Slippage detected")
            # reset references
            self.last_scan_range = range_val
            self.last_odom_x = None
            self.last_odom_y = None
            self.odom_move = 0.0


def main(args=None):
    rclpy.init(args=args)
    node = SlipDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
