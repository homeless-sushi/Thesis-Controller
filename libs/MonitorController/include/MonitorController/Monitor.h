#ifndef MONITOR_CONTROLLER_MONITOR
#define MONITOR_CONTROLLER_MONITOR

#include <vector>

#include <sys/types.h>

#include "MonitorCommon/Monitor.h"

//initialize and destroy monitor_t data structure
monitor_t* monitorInit(int numOfCores);
void monitorDestroy(monitor_t* monitor);
//read (copy!) data_t values from the shared memory given a segment id
data_t monitorRead(int segmentId);
//get a reference of the shared memory given a segment id
data_t* monitorPtrRead(int segmentId);

//get current and global throughput
double getGlobalThroughput(data_t* data);
double getCurrThroughput(data_t* data, int TPwindow = DEFAULT_TIME_WINDOW);
//get current required throughput
double getReqThroughput(data_t* data);
//setters of various flags
void setUseGPU(data_t* data, bool value);
void setPrecisionLevel(data_t* data, int value);
void setUsleepTime(data_t* data, int value);
void setNumThreads(data_t* data, int value);

//print the status of the attached applications
void printAttachedApplications(monitor_t* monitor);
//update the status (we have to call it at the beginning of the control loop). the last flag says if we have to look for died applications
std::vector<pid_t> updateAttachedApplications(monitor_t* monitor, bool check_died = true);
//check if a give application is running or not
bool isRunning(pid_t pid);
//kill all attached applications
void killAttachedApplications(monitor_t* monitor);
//Get thread ids of the running application, in order to apply cgroups policy
std::vector<pid_t> getAppPids(pid_t appPid);
//Return true if the application is an OpenCL/OpenMP/OpenCV one; otherwise false.
bool isOpenX(monitor_t* monitor, pid_t pid);
//Set CPU cores where to run the application. WRAPPER to CGroups
void UpdateCpuSet(monitor_t* monitor, pid_t pid, std::vector<int> cores);
//Set CPU quota where to run the application. WRAPPER to CGroups
void UpdateCpuQuota(monitor_t* monitor, pid_t pid, float quota);

#endif //MONITOR_CONTROLLER_MONITOR