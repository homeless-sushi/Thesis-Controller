#include "MonitorPolicy.h"

#include <iostream>

#include <string.h>
#include <unistd.h>
#include <sys/shm.h>
#include <sys/time.h>

#include "MonitorCommon/Monitor.h"
#include "MonitorController/Monitor.h"
#include "MonitorController/Policy.h"
#include "MonitorController/CGroupUtils.h"
#include "MonitorController/Utilization.h"

#define CHANGEPERIOD 10
#define NUM_CORES 16

MonitorPolicy::MonitorPolicy(bool sensorsEnabled) {
    this->appl_monitor = monitorInit(NUM_CORES);
    this->sensorsEnabled = sensorsEnabled;
    if(sensorsEnabled)
        this->utilization = new Utilization(NUM_CORES);
}

MonitorPolicy::~MonitorPolicy(){  
    killAttachedApplications(this->appl_monitor);
    monitorDestroy(this->appl_monitor);
    if(sensorsEnabled)
        delete utilization;
}

void MonitorPolicy::run(int cycle){
    std::vector<pid_t> newAppls = updateAttachedApplications(this->appl_monitor);
    
    if(newAppls.size()>0){    
        std::cout << "New applications: ";
        for(int i=0; i < newAppls.size(); i++)
            std::cout << newAppls[i] << " ";

        std::cout << std::endl;
    }
    
    //run resource management policy
    printAttachedApplications(this->appl_monitor);

    if(sensorsEnabled){
        std::vector<int> utilizations = utilization->computeUtilization();  
        
        std::cout << "CPU usage: ";
        for(int j=0; j < utilizations.size(); j++)
            std::cout << utilizations[j] << " ";
        
        std::cout << std::endl;
    }
    
    if(cycle%CHANGEPERIOD == 0){
        std::vector<int> cores;
        std::cout << "CAMBIO MAPPING!" << std::endl;

        if(cycle/CHANGEPERIOD%2==0){
            cores.push_back(0);   
        }else{
            cores.push_back(1); 
        }   

        for(int i=0; i < appl_monitor->nAttached; i++){
            UpdateCpuSet(this->appl_monitor, appl_monitor->appls[i].pid, cores);
        }
    }
}
