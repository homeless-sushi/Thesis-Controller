#ifndef MONITOR_COMMON_MONITOR
#define MONITOR_COMMON_MONITOR

#include <sched.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/sem.h>

#ifdef __cplusplus
#include <vector>
#endif

//C code
//include bool type definition
#ifndef __cplusplus
#include <stdbool.h>
#endif

//constants with maximum sizes for the various sets (implemented by using static arrays for simplicity since stored in a shared memory)
#define MAX_TICKS_SIZE 300
#define MAX_NUM_OF_APPLS 128
#define MAX_NUM_OF_CPU_SETS 32
#define MAX_NAME_SIZE 100
#define DEFAULT_TIME_WINDOW 1
#define DEFAULT_CONTROLLER_NAME "controller"
#define ZERO_APPROX 1e-5

/*
 * tick_t type is used to collect heartbeat
 */
typedef struct {
  long long   value; //number of accumulated ticks
  long double time;  //since the start time of the application
} tick_t;

/*
 * data_t type is used to specify the data (saved in the shared memory) exchanged between the controller and the application during the execution (performance data and actuation values).
 * A segment in the shared memory is created for each application
 */
typedef struct {
  int         segmentId;             // id of the memory segment where this structure is stored
  long double startTime;             // logged start time of the application
  //monitoring
  tick_t      ticks[MAX_TICKS_SIZE]; // vector of ticks. Actually this vector is used as a sliding window for efficiency reasons. therefore we have following pointers
  int         curr;                  // "pointer" to the current position where the last tick has been saved
  //requirement
  long double reqThr;                //  throughput to be guaranteed (if equal to 0, it is not set)
  //actuation
  long double  lastTimeSample;       // last timestamp that has been sampled. it is necessary to implement the autosleep function
  bool         useGPU;               // GPU/notCPU
  int          usleepTime;           //in microseconds
  int          precisionLevel;       //0:exact computation; >0 approximate computation. it represents the percentage of approximation
  int          numThreads;           //number of threads to set- ak
} data_t;

/*
 * appl_t type is used as a descriptor of an application.
 */
typedef struct {
  pid_t       pid;                   // application pid
  char        name[MAX_NAME_SIZE+1]; // name of the application
  int         segmentId;             // id of the memory segment containing the corresponding data_t structure
  bool        isOpenX;               // specify if the application is an OpenCL/OpenMP/OpenCV one. in such a case threads have to be forced separaterly with Cgroups.
  bool        gpuImpl;               // has a GPU implementation or not
  int         maxThreads;            // 1= serial implementation; >1 parallel implementation
  int         mapping;               // 0=LITTLE, 1=big, 2=GPU
  bool        alreadyInit;    // states if CGroups have been already initialized by the controller for the application or not
  //this last field is used to understand if cgroups have been already configured for each registered application.
  //indeed we don't have a way for an application to signal the controller on the registration.
  //therefore the controller use to check periodically the application table (i.e. the monitor structure in the shared memory)
  //to detect new applications and configure them
  //DO NOTE: according to this asynchronous scheme it is necessary to check for new applications with a quite high frequency (1 sec);
  //then we should run the resource management policy with a lower frequency
} appl_t;

/*
 * monitor_t type is used to contain the status of the system (regarding to the running applications).
 * a single data structure is allocated for a controller and it is stored in a shared memory (just because in this way the transmission of the appl_t descriptor is easier).
 * TODO this may be refactored in some more efficient way
 */
typedef struct {
  //set of monitored applications
  appl_t  appls[MAX_NUM_OF_APPLS];
  int     nAttached; //current number of monitored applications

  //set of applications that have been detached recently. necessary to update above appls set
  pid_t   detached[MAX_NUM_OF_APPLS];
  int     nDetached; //current number of detached applications
} monitor_t;

//semaphore management, data structure and wait/post functions.
//The semaphore is used to access the monotor_t data structure in the shared memory since both the applications and the controller may write it
union semun {
  int                val;
  struct semid_ds    *buf;
  unsigned short int *array;
  struct seminfo     *__buf;
};

#endif //MONITOR_COMMON_MONITOR