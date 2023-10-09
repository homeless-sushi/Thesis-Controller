# When the project is built, create this library
add_library(CONTROLLER_Policies_LIB)

# Add sources
target_sources(CONTROLLER_Policies_LIB
    PRIVATE
        "src/ExamplePolicy.cc"
        "src/GpuInterferencePolicy.cc"
        "src/CpuPowerModelPolicy.cc"
        "src/GpuPowerModelPolicy.cc"
        "src/CpuProfilingPolicy.cc"
        "src/SetConfigurationPolicy.cc"
)

# Add to the include path
target_include_directories(CONTROLLER_Policies_LIB 
    PUBLIC
        "include"
)

target_link_libraries(CONTROLLER_Policies_LIB PUBLIC CONTROLLER_Utils_LIB)

# Add Runtime Manager dependency
target_link_libraries(CONTROLLER_Policies_LIB PUBLIC AppRegister_Common_Lib)
target_link_libraries(CONTROLLER_Policies_LIB PUBLIC AppRegister_Server_Lib)
