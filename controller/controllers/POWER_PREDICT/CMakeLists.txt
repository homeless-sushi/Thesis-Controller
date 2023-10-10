# Add the controller executable
add_executable(PowerPredictController
    "src/main.cc"
)

# Rename the executable file
set_target_properties(PowerPredictController 
    PROPERTIES 
        OUTPUT_NAME "RtrmController")

# Add Policies
target_link_libraries(PowerPredictController PUBLIC CONTROLLER_Policies_LIB)

# Add Runtime Manager dependency
target_link_libraries(PowerPredictController PUBLIC AppRegister_Common_Lib)
target_link_libraries(PowerPredictController PUBLIC AppRegister_Server_Lib)

# Add Boost Libraries
target_include_directories(PowerPredictController PUBLIC ${Boost_INCLUDE_DIR})
target_link_libraries(PowerPredictController PUBLIC ${Boost_LIBRARIES})