# Add the controller executable
add_executable(CpuProfilingController
    "src/main.cc"
)

# Rename the executable file
set_target_properties(CpuProfilingController 
    PROPERTIES 
        OUTPUT_NAME "RtrmController")

# Add Policies
target_link_libraries(CpuProfilingController PUBLIC CONTROLLER_Policies_LIB)

# Add Runtime Manager dependency
target_link_libraries(CpuProfilingController PUBLIC AppRegister_Common_Lib)
target_link_libraries(CpuProfilingController PUBLIC AppRegister_Server_Lib)

# Add Boost Libraries
target_include_directories(CpuProfilingController PUBLIC ${Boost_INCLUDE_DIR})
target_link_libraries(CpuProfilingController PUBLIC ${Boost_LIBRARIES})