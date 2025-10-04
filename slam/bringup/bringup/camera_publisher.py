#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
import cv2
import numpy as np

class CameraPublisher(Node):
    def __init__(self):
        super().__init__('camera_publisher')
        self.publisher_ = self.create_publisher(CompressedImage, 'camera/image/compressed', 10)

        # Timer for 10 FPS
        self.timer = self.create_timer(1/10, self.timer_callback)

        self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 416) 
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 416)
        self.cap.set(cv2.CAP_PROP_FPS, 10)

        if not self.cap.isOpened():
            self.get_logger().error('Could not open camera')
        else:
            self.get_logger().info('Camera publisher ready')

    def timer_callback(self):
        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().error('Failed to capture image')
            return

        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 80]
        success, buffer = cv2.imencode('.jpg', frame, encode_param)
        if not success:
            self.get_logger().error('Failed to encode image')
            return

        msg = CompressedImage()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.format = "jpeg"
        msg.data = buffer.tobytes()

        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = CameraPublisher()
    rclpy.spin(node)
    node.cap.release()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
