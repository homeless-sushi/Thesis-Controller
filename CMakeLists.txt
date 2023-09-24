# Set CMake Version
cmake_minimum_required(VERSION 3.7...3.25)

# Set CMake Policy (automatically set to version if VERSION >= 3.12)
if(${CMAKE_VERSION} VERSION_LESS 3.12)
    cmake_policy(VERSION ${CMAKE_MAJOR_VERSION}.${CMAKE_MINOR_VERSION})
endif()

#Project name
project(RtrmController)

#When the project is built, create this executable
add_executable(RtrmController
        "src/main.cc"
        "src/SensingPolicy.cc"
        "src/DummyPolicy.cc"
)
target_include_directories(RtrmController
    PRIVATE
        "include"
)

#TODO: Use find_package(); for this, the communication libraries have to be setup 
#      with a cmake configuration file.
#
set(RtrmCommunication_DIR "/home/miele/Vivian/Thesis/Thesis-Communication")
add_subdirectory(${RtrmCommunication_DIR} "${RtrmCommunication_DIR}/build")
target_link_libraries(RtrmController PUBLIC AppRegister_Common_Lib)
target_link_libraries(RtrmController PUBLIC AppRegister_Server_Lib)
