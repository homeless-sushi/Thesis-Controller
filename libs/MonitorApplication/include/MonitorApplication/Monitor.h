#ifndef MONITOR_APP_MONITOR
#define MONITOR_APP_MONITOR

#include "MonitorCommon/Monitor.h"

//C code
//include bool type definition
#ifndef __cplusplus
#include <stdbool.h>
#endif

#ifdef __cplusplus
extern "C"
{
#endif
//Attach the application to the monitor
data_t* monitorAttach(const char* applName, long double req_thr, int mapping, int maxThreads, bool isOpenX);
//Detach the application from the monitor
int monitorDetach(data_t *data);
//Send a tick to the monitor which the application is connected
void monitorTick(data_t *data, int value);

//Sleep for a given amount of time to satisfy the required throughput
void autosleep(data_t* data, long double ref_thr);

//Set new throughput
void setReqThroughput(data_t* data, long double reqThr);
//Get the current device to be used true=GPU/false=CPU
bool getGPU(data_t *data);
//Get the usleep time
int getSleepTime(data_t* data);
//Get the current precision level to be used (0 maximum - 100 minimum)
int getPrecisionLevel(data_t *data);
//Get the number of threads of an application (preferably multiples of 2)
int getNumThreads(data_t *data);
//Get the controller pid given its name
pid_t getMonitorPid(const char*);


#ifdef __cplusplus
}
#endif

#endif //MONITOR_APP_MONITOR
