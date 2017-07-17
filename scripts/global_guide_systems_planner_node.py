#!/usr/bin/env python

import sys
import os
# Prevent pyc files being generated!
sys.dont_write_bytecode = True

sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + '/../lib/vaarkaart'))
sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + '/../lib/astar'))
sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + '/../lib/graph'))
sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + '/../lib/globalguidesystems'))

import rospy

import vaarkaart_loader

from global_guide_systems_planner import GlobalGuideSystemsPlanner

if __name__ == "__main__":
    rospy.init_node('global_guide_systems_planner_node')

    print "Loading vaarkaart"
    vaarkaart_graph = vaarkaart_loader.load_vaarkaart()

    global_guide_systems_planner = GlobalGuideSystemsPlanner(vaarkaart_graph)
        
    global_guide_systems_planner.path_regression()

    rospy.spin()