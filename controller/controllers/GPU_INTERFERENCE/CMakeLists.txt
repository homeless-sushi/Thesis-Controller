# Add the controller executable
add_executable(GpuInterferenceController
    "src/main.cc"
)

# Rename the executable file
set_target_properties(GpuInterferenceController 
    PROPERTIES 
        OUTPUT_NAME "RtrmController")

# Add Policies
target_link_libraries(GpuInterferenceController PUBLIC CONTROLLER_Policies_LIB)

# Add Runtime Manager dependency
target_link_libraries(GpuInterferenceController PUBLIC AppRegister_Common_Lib)
target_link_libraries(GpuInterferenceController PUBLIC AppRegister_Server_Lib)

# Add Boost Libraries
target_include_directories(GpuInterferenceController PUBLIC ${Boost_INCLUDE_DIR})
target_link_libraries(GpuInterferenceController PUBLIC ${Boost_LIBRARIES})