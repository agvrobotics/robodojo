######################on Raspberry PI###########################
cd ~/robodojo/slam
tmux new -s bringup
source install/setup.bash
ros2 launch bringup bringup.launch.py

cd ~/slam1/ros2_ws
tmux new -s rplidar
source install/setup.bash
ros2 launch rplidar_ros rplidar_a1_launch.py serial_port:=/dev/ttyUSB0 serial_baudrate:=115200 frame_id:=lidar_llink_1

##################On PC###########################
cd ~/Documents/robodojo/slam
source install/setup.bash
ros2 launch bringup teleop.launch.py

cd ~/Documents/robodojo/slam
source install/setup.bash
ros2 launch dekutamr_description display.launch.py

cd ~/Documents/robodojo/slam
source install/setup.bash
ros2 launch bringup slam.async.launch.py

##--------------confirm tree structure----------------##
ros2 run tf2_tools view_frames

#####LOADING A MAP#####
#METHOD 1: using slamtoolbox in localization mode
ros2 launch bringup slam.localization.launch.py

#METHOD 2: using map server
#This method is unreliable, sometimes it works, sometimes it doesn't -> set durability in topic to transient local
ros2 run nav2_map_server map_server --ros-args -p yaml_filename:=/home/sierra-95/Documents/robodojo/slam/michael_save.yaml 
ros2 run nav2_util lifecycle_bringup map_server 
#amcl for localisation
ros2 run nav2_amcl amcl
ros2 param list /amcl
ros2 param get /amcl base_frame_id
ros2 param set /amcl base_frame_id base_link

#METHOD 3: using nav2_bringup
ros2 launch nav2_bringup localization_launch.py map:=/home/sierra-95/Documents/robodojo/slam/bringup.yaml use_sim_time:=false
fixed_frame: "map"
ros2 param set /amcl base_frame_id base_link
ros2 launch nav2_bringup navigation_launch.py use_sim_time:=false map_subscribe_transient_local:=true params_file:=/home/sierra-95/Documents/robodojo/slam/bringup/params/nav2_params.yaml
