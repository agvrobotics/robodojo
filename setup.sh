######################on Raspberry PI###########################
cd ~/robodojo/slam
tmux new -s bringup
source install/setup.bash
ros2 launch bringup bringup.launch.py

cd ~/slam1/ros2_ws
tmux new -s rplidar
source install/setup.bash
ros2 launch rplidar_ros rplidar_a1_launch.py serial_port:=/dev/ttyUSB0 serial_baudrate:=115200 frame_id:=lidar_link_1

##########OLD TELEOP###############
cd ~/robodojo/motor_control/Motion_V2/ros_ws
tmux new -s teleop
source install/setup.bash
ros2 run agv_control keyboard_teleop
##################################


##################On PC###########################
cd ~/Documents/robodojo/slam
source install/setup.bash
ros2 launch dekut_amr_description display.launch.py
ros2 launch bringup slam.launch.py

##--------------confirm tree structure----------------##
ros2 run tf2_tools view_frames

#### NAV2 #########################
ros2 launch nav2_bringup localization_launch.py map:=/home/sierra-95/Documents/robodojo/slam/bringup.yaml use_sim_time:=false
ros2 launch nav2_bringup navigation_launch.py params_file:=/home/sierra-95/Documents/robodojo/slam/bringup/params/nav2_params.yaml use_sim_time:=false