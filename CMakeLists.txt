cmake_minimum_required(VERSION 2.8.3)
project(nautonomous_navigation_planner_global)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  geometry_msgs
)

catkin_package(

)

include_directories(
  ${catkin_INCLUDE_DIRS}
  lib/vaarkaart
  lib/astar
  lib/graph
  lib/globalguidesystems
)
