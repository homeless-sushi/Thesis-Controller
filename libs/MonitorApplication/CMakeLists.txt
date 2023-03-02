#When the project is built, create this library
add_library(Monitor_Application_Lib STATIC
    "src/Monitor.cc")

#Add to the include path
target_include_directories(Monitor_Application_Lib PUBLIC "include")

#Add Monitor Common dependency
target_link_libraries(Monitor_Application_Lib Monitor_Common_Lib)
