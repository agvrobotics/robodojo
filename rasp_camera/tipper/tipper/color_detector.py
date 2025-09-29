import rclpy
from rclpy.node import Node
import cv2, yaml, time
import numpy as np
from std_msgs.msg import String

class ColorDetector(Node):
    def __init__(self):
        super().__init__('color_detector')

        # Load HSV ranges
        with open('/home/sierra-95/Documents/robodojo/rasp_camera/tipper/params/colors.yaml', 'r') as f:
            cfg = yaml.safe_load(f)
        self.red_ranges  = [(np.array(v[:3]), np.array(v[3:])) for v in cfg['red']]
        self.blue_ranges = [(np.array(v[:3]), np.array(v[3:])) for v in cfg['blue']]

        # Camera
        self.cap = cv2.VideoCapture('/dev/video0')

        # ROS publisher
        self.pub = self.create_publisher(String, '/tipper_cmd', 10)

        # Timing
        self.last_trigger_time = 0.0       # time of last 1 message
        self.cooldown = 5.0                # min time between new triggers
        self.pending_close_time = None     # when to send 0

        self.timer = self.create_timer(0.1, self.process_frame)

    def detect_color(self, hsv, ranges):
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for lower, upper in ranges:
            mask |= cv2.inRange(hsv, lower, upper)
        return mask

    def process_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        frame = cv2.resize(frame, (640, int(frame.shape[0]*640/frame.shape[1])))
        h, w, _ = frame.shape
        box_size = 200
        x1, y1 = w//2 - box_size//2, h//2 - box_size//2
        x2, y2 = w//2 + box_size//2, h//2 + box_size//2
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255,255,255), 2)

        roi = frame[y1:y2, x1:x2]
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        red_mask  = self.detect_color(hsv, self.red_ranges)
        blue_mask = self.detect_color(hsv, self.blue_ranges)

        now = time.time()

        # ---- Detect color and send "1" ----
        if (cv2.countNonZero(red_mask) > 5000 or cv2.countNonZero(blue_mask) > 5000):
            if (now - self.last_trigger_time) > self.cooldown:
                self.pub.publish(String(data="1"))
                self.last_trigger_time = now
                self.pending_close_time = now + 3.0  # schedule close after 3 seconds

        # ---- If 3 seconds passed, send "0" ----
        if self.pending_close_time and now >= self.pending_close_time:
            self.pub.publish(String(data="0"))
            self.pending_close_time = None

        cv2.imshow("Camera View", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            rclpy.shutdown()

    def destroy_node(self):
        self.cap.release()
        cv2.destroyAllWindows()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = ColorDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
