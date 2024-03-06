# When the project is built, create this library
add_library(CONTROLLER_FinalPolicy_LIB)

# Add sources
target_sources(CONTROLLER_FinalPolicy_LIB
    PRIVATE
        "src/FinalPolicy.cc"
)

# Add to the include path
target_include_directories(CONTROLLER_FinalPolicy_LIB 
    PUBLIC
        "include"
)

target_link_libraries(CONTROLLER_FinalPolicy_LIB PUBLIC CONTROLLER_Utils_LIB)

# Add Runtime Manager dependency
target_link_libraries(CONTROLLER_FinalPolicy_LIB PUBLIC AppRegister_Common_Lib)
target_link_libraries(CONTROLLER_FinalPolicy_LIB PUBLIC AppRegister_Server_Lib)
