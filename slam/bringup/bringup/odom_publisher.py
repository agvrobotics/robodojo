#!/usr/bin/env python3

import math
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from std_msgs.msg import Int32MultiArray
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
import tf_transformations


class DiffOdomPublisher(Node):
    def __init__(self):
        super().__init__('diff_odom_publisher')

        # --- Parameters ---
        self.declare_parameter('wheel_radius', 0.0425)      # meters
        self.declare_parameter('wheel_separation', 0.2325)  # meters
        self.declare_parameter('counts_per_rev', 4100)
        self.declare_parameter('publish_hz', 20.0)
        self.declare_parameter('smoothing_alpha', 0.3)
        self.declare_parameter('odom_frame', 'odom')
        self.declare_parameter('base_frame', 'base_link')

        # Load params
        self.wheel_radius = self.get_parameter('wheel_radius').value
        self.wheel_separation = self.get_parameter('wheel_separation').value
        self.counts_per_rev = self.get_parameter('counts_per_rev').value
        self.publish_hz = self.get_parameter('publish_hz').value
        self.alpha = self.get_parameter('smoothing_alpha').value
        self.odom_frame = self.get_parameter('odom_frame').value
        self.base_frame = self.get_parameter('base_frame').value

        # Internal state
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0

        self.v = 0.0
        self.omega = 0.0

        self.last_counts = None
        self.last_time = None

        # ticks to meters conversion
        self.ticks_to_m = (2 * math.pi * self.wheel_radius) / self.counts_per_rev

        # ROS interfaces
        self.tf_broadcaster = TransformBroadcaster(self)
        self.odom_pub = self.create_publisher(Odometry, 'odom', 10)
        self.create_subscription(Int32MultiArray, 'encoder_counts', self.encoder_cb, 10)

        # Timer
        self.create_timer(1.0 / self.publish_hz, self.publish_odom)

        self.get_logger().info("Diff Odom Publisher Ready")


    # ---------------------- ENCODER CALLBACK ----------------------
    def encoder_cb(self, msg):
        # msg.data = [left, right]
        if len(msg.data) < 2:
            return

        left_ticks = int(msg.data[0])
        right_ticks = int(msg.data[1])

        now = self.get_clock().now()

        if self.last_counts is None:
            self.last_counts = [left_ticks, right_ticks]
            self.last_time = now
            return

        # Time diff
        dt = (now - self.last_time).nanoseconds * 1e-9
        if dt <= 0.0:
            return

        # Tick difference
        dL = left_ticks - self.last_counts[0]
        dR = right_ticks - self.last_counts[1]

        # Convert ticks → meters
        distL = dL * self.ticks_to_m
        distR = dR * self.ticks_to_m

        # Compute velocities
        raw_v = (distL + distR) / (2.0 * dt)
        raw_omega = (distR - distL) / (self.wheel_separation * dt)

        # EMA smoothing
        self.v = self.alpha * raw_v + (1 - self.alpha) * self.v
        self.omega = self.alpha * raw_omega + (1 - self.alpha) * self.omega

        # Integrate pose
        self.x += self.v * math.cos(self.theta) * dt
        self.y += self.v * math.sin(self.theta) * dt
        self.theta = (self.theta + self.omega * dt + math.pi) % (2 * math.pi) - math.pi

        # Update
        self.last_counts = [left_ticks, right_ticks]
        self.last_time = now


    # ---------------------- ODOM PUBLISH ----------------------
    def publish_odom(self):
        if self.last_time is None:
            return

        now = self.get_clock().now()

        # TF transform
        t = TransformStamped()
        t.header.stamp = now.to_msg()
        t.header.frame_id = self.odom_frame
        t.child_frame_id = self.base_frame
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.translation.z = 0.0

        q = tf_transformations.quaternion_from_euler(0, 0, self.theta)
        t.transform.rotation.x = q[0]
        t.transform.rotation.y = q[1]
        t.transform.rotation.z = q[2]
        t.transform.rotation.w = q[3]

        self.tf_broadcaster.sendTransform(t)

        # Odometry msg
        odom = Odometry()
        odom.header.stamp = now.to_msg()
        odom.header.frame_id = self.odom_frame
        odom.child_frame_id = self.base_frame

        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.orientation.x = q[0]
        odom.pose.pose.orientation.y = q[1]
        odom.pose.pose.orientation.z = q[2]
        odom.pose.pose.orientation.w = q[3]

        odom.twist.twist.linear.x = self.v
        odom.twist.twist.angular.z = self.omega

        self.odom_pub.publish(odom)


def main(args=None):
    rclpy.init(args=args)
    node = DiffOdomPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
