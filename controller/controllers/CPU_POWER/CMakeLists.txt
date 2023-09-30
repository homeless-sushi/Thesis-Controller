# Add the controller executable
add_executable(CpuPowerModelController
    "src/main.cc"
)

# Rename the executable file
set_target_properties(CpuPowerModelController 
    PROPERTIES 
        OUTPUT_NAME "RtrmController")

# Add Policies
target_link_libraries(CpuPowerModelController PUBLIC CONTROLLER_Policies_LIB)

# Add Runtime Manager dependency
target_link_libraries(CpuPowerModelController PUBLIC AppRegister_Common_Lib)
target_link_libraries(CpuPowerModelController PUBLIC AppRegister_Server_Lib)

# Add Boost Libraries
target_include_directories(CpuPowerModelController PUBLIC ${Boost_INCLUDE_DIR})
target_link_libraries(CpuPowerModelController PUBLIC ${Boost_LIBRARIES})