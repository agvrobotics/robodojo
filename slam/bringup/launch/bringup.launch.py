from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='bringup',
            executable='serial_node',
            output='screen',
            parameters=[{
               'port': '/dev/ttyACM0',
                'baudrate': 115200
            }]
        ),
        Node(
            package='bringup',
            executable='odom_publisher',
            output='screen'
        ),
        Node(
            package='bringup',
            executable='slip_detector',
            output='screen'
        )
    ])
