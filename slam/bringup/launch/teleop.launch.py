from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='joy',
            executable='joy_node',
            name='joy_node',
            output='screen',
            parameters=[{'dev': '/dev/input/js0'}]
        ),
        Node(
            package='teleop_twist_joy',
            executable='teleop_node',
            name='teleop_twist_joy_node',
            output='screen',
            parameters=[{
                'axis_linear.x': 1,
                'scale_linear.x': 0.25,
                'axis_angular.yaw': 0,
                'scale_angular.yaw': 1.9,
                'enable_button': 4,
                'enable_turbo_button': 5,
                'scale_linear_turbo.x': 0.425, #Linear with turbo
                'scale_angular_turbo.yaw': 2.99 #Angular with turbo
            }],
            remappings=[('/cmd_vel', '/joy_vel')]
        ),
        Node(
            package='twist_mux',
            executable='twist_mux',
            name='twist_mux',
            output='screen',
            parameters=[
                '/home/sierra-95/Documents/robodojo/slam/bringup/params/twist_mux_topics.yaml'                      
            ],
        )
    ])
