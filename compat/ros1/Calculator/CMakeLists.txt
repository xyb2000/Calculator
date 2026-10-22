cmake_minimum_required(VERSION 3.0.2)
project(Calculator)

find_package(catkin REQUIRED COMPONENTS message_generation rospy std_msgs)

catkin_python_setup()

add_service_files(FILES AddTwoInts.srv)
generate_messages()

catkin_package(CATKIN_DEPENDS message_runtime rospy std_msgs)

catkin_install_python(PROGRAMS
  scripts/add_two_ints_server.py
  scripts/add_two_ints_client.py
  scripts/talker.py
  scripts/listener.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(DIRECTORY launch
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

if(CATKIN_ENABLE_TESTING)
  find_package(rostest REQUIRED)
  catkin_install_python(PROGRAMS test/test_add_two_ints.py
    DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
  )
  add_rostest(test/add_two_ints.test)
endif()
