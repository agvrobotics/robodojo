from setuptools import find_packages, setup

package_name = 'bringup'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', [
            'launch/slam.async.launch.py',
            'launch/slam.localization.launch.py',
            'launch/bringup.launch.py',
            'launch/teleop.launch.py'
        ]),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='sierra-95',
    maintainer_email='michaelmachohi@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'odom_publisher = bringup.odom_publisher:main',
            'serial_node = bringup.serial_node:main',
            'keyboard_teleop = bringup.keyboard_teleop:main',
            'tipper_joy = bringup.tipper_joy:main',
            'camera_publisher = bringup.camera_publisher:main',
        ],
    },
)
