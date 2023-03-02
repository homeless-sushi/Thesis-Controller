#When the project is built, create this library
add_library(Monitor_Controller_Lib STATIC
    "src/Monitor.cc"
    "src/Utilization.cc"
    "src/CGroupUtils.cc")

#Add to the include path
target_include_directories(Monitor_Common_Lib PUBLIC "include")

#Add the these libraries as dipendencies
target_link_libraries(Monitor_Controller_Lib PUBLIC Monitor_Common_Lib)
target_link_libraries(Monitor_Controller_Lib PUBLIC cgroup)