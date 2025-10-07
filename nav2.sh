ros2 run nav2_map_server --ros-args -p yaml_filename:=/home/sierra-95/Documents/robodojo/slam/michael.yaml
ros2 lifecycle nodes
ros2 lifecycle get /map_server
ros2 lifecycle set /map_server 1 # configure
ros2 lifecycle set /map_server 3 # activate

#checking QOS on /map
ros2 topic info /map --verbose