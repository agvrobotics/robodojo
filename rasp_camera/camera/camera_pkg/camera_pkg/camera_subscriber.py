#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np

class CameraSubscriber(Node):
    def __init__(self):
        super().__init__('camera_subscriber')
        self.subscription = self.create_subscription(
            Image,
            'camera/image_raw',
            self.listener_callback,
            10  # queue size
        )
        self.subscription 
        self.bridge = CvBridge()

        self.color_ranges = {
            "red":    ([0, 120, 70], [10, 255, 255]),
            "green":  ([40, 50, 50], [90, 255, 255]),
            "blue":   ([100, 150, 0], [140, 255, 255]),
            "yellow": ([20, 100, 100], [30, 255, 255]),
            "orange": ([10, 100, 20], [25, 255, 255]),
        }

    def listener_callback(self, msg):
        # Convert ROS Image -> OpenCV
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")

        if frame is not None:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Region of interest (center 100x100 px)
            h, w, _ = hsv.shape
            roi = hsv[h//2-50:h//2+50, w//2-50:w//2+50]

            detected_color = "None"
            for color, (lower, upper) in self.color_ranges.items():
                lower = np.array(lower)
                upper = np.array(upper)
                mask = cv2.inRange(roi, lower, upper)
                if cv2.countNonZero(mask) > 500:
                    detected_color = color
                    break

            print("Detected Color:", detected_color)
            cv2.rectangle(frame, (w//2-50, h//2-50), (w//2+50, h//2+50), (255,255,255), 2)
            cv2.imshow("Camera Subscriber (Raw)", frame)
            cv2.waitKey(1)
        else:
            self.get_logger().warn("Failed to convert image")

def main(args=None):
    rclpy.init(args=args)
    node = CameraSubscriber()
    rclpy.spin(node)
    cv2.destroyAllWindows()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
