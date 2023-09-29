# Add the controller executable
add_executable(ExampleController
    "src/main.cc"
)

# Rename the executable file
set_target_properties(ExampleController 
    PROPERTIES 
        OUTPUT_NAME "RtrmController")

# Add Policies
target_link_libraries(ExampleController PUBLIC CONTROLLER_Policies_LIB)

# Add Runtime Manager dependency
target_link_libraries(ExampleController PUBLIC AppRegister_Common_Lib)
target_link_libraries(ExampleController PUBLIC AppRegister_Server_Lib)

# Add Boost Libraries
target_include_directories(ExampleController PUBLIC ${Boost_INCLUDE_DIR})
target_link_libraries(ExampleController PUBLIC ${Boost_LIBRARIES})