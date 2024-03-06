# Add the controller executable
add_executable(FinalController
    "src/main.cc"
)

# Rename the executable file
set_target_properties(FinalController 
    PROPERTIES 
        OUTPUT_NAME "RtrmController")

# Add Policies
target_link_libraries(FinalController PUBLIC CONTROLLER_FinalPolicy_LIB)

# Add Runtime Manager dependency
target_link_libraries(FinalController PUBLIC AppRegister_Common_Lib)
target_link_libraries(FinalController PUBLIC AppRegister_Server_Lib)

# Add Boost Libraries
target_include_directories(FinalController PUBLIC ${Boost_INCLUDE_DIR})
target_link_libraries(FinalController PUBLIC ${Boost_LIBRARIES})