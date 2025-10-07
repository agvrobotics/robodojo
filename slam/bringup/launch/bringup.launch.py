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
            executable='camera_publisher',
            output='screen',
        ),
        # Node(
        #     package='slam_toolbox',
        #     executable='async_slam_toolbox_node',
        #     name='slam_toolbox',
        #     output='screen',
        #     parameters=[
        #         '/home/agv/robodojo/slam/bringup/params/mapper_params_online_async.yaml',
        #         {'use_sim_time': False}
        #     ]
        # ),
    ])
