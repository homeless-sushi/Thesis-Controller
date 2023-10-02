# Add the controller executable
add_executable(GpuPowerModelController
    "src/main.cc"
)

# Rename the executable file
set_target_properties(GpuPowerModelController 
    PROPERTIES 
        OUTPUT_NAME "RtrmController")

# Add Policies
target_link_libraries(GpuPowerModelController PUBLIC CONTROLLER_Policies_LIB)

# Add Runtime Manager dependency
target_link_libraries(GpuPowerModelController PUBLIC AppRegister_Common_Lib)
target_link_libraries(GpuPowerModelController PUBLIC AppRegister_Server_Lib)

# Add Boost Libraries
target_include_directories(GpuPowerModelController PUBLIC ${Boost_INCLUDE_DIR})
target_link_libraries(GpuPowerModelController PUBLIC ${Boost_LIBRARIES})