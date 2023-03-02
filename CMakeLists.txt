# Set CMake Version
cmake_minimum_required(VERSION 3.7...3.25)

# Set CMake Policy (automatically set to version if VERSION >= 3.12)
if(${CMAKE_VERSION} VERSION_LESS 3.12)
    cmake_policy(VERSION ${CMAKE_MAJOR_VERSION}.${CMAKE_MINOR_VERSION})
endif()

#Project name
project(RtrmProject)

#When the project is built, create these executables
add_executable(RtrmApp
    "src/main.cc"
    "src/MonitorPolicy.cc")

#Include these headers
target_include_directories(RtrmApp PUBLIC "include")

#Run the CMake of libs/MonitorApplication
add_subdirectory("libs/MonitorApplication")

#Run the CMake of libs/HMLSS_BFS, then add the generated library as dipendency
add_subdirectory("libs/MonitorCommon")
target_link_libraries(RtrmApp PUBLIC Monitor_Common_Lib)

#Run the CMake of libs/MonitorController, then add the generated library as dipendency
add_subdirectory("libs/MonitorController")
target_link_libraries(RtrmApp PUBLIC Monitor_Controller_Lib)