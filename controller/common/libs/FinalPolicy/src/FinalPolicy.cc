#include "FinalPolicy/FinalPolicy.h"

#include <iostream>
#include <iterator>
#include <map>
#include <memory>
#include <set>
#include <sstream>
#include <vector>

#include "AppRegisterServer/App.h"
#include "AppRegisterServer/AppData.h"
#include "AppRegisterServer/Policy.h"
#include "AppRegisterServer/Sensors.h"
#include "AppRegisterServer/Utilization.h"
#include "AppRegisterServer/Frequency.h"
#include "AppRegisterServer/CGroupUtils.h"

namespace Policy
{
    FinalPolicy::FinalPolicy(
        unsigned nCores,
        std::string controllerLogUrl,
        std::string sensorsLogUrl
    ) :
        Policy(nCores),
        controllerLogFile(controllerLogUrl, controllerLogFile.out),
        utilization(nCores),
        sensorLogFile(sensorsLogUrl, sensorLogFile.out)
    {
        //Frequency::SetCpuFreq(Frequency::getMinCpuFreq());
        //Frequency::SetGpuFreq(Frequency::getMinGpuFreq());

        controllerLogFile << "CYCLE,PID,NAME,TARGET,CURRENT" << std::endl;

        sensorLogFile << "CYCLE,";
        for(unsigned i = 0; i < nCores; ++i)
            sensorLogFile << "UTILIZATION_" << i << ",";
        sensorLogFile << "CPUFREQ,GPUFREQ,SOCW,CPUW,GPUW" << std::endl;
    };

    void FinalPolicy::run(int cycle)
    {
        lock();

        //Deregister detached and dead apps
        std::vector<pid_t> deregisteredApps;
        std::vector<pid_t> detachedApps(deregisterDetachedApps());
        deregisteredApps.insert(std::end(deregisteredApps), std::begin(detachedApps), std::end(detachedApps));
        std::vector<pid_t> deadApps(deregisterDeadApps());
        deregisteredApps.insert(std::end(deregisteredApps), std::begin(deadApps), std::end(deadApps));
//      std::vector<pid_t> newAppsVec(registerNewApps());
//      std::copy(newAppsVec.begin(),newAppsVec.end(), std::inserter(newRegisteredApps, newRegisteredApps.end()));
        for(pid_t deregisteredApp : deregisteredApps){
            runningApps.erase(deregisteredApp);
        }

        //Save currentThroughput for later
        std::map<pid_t, long double> currentThroughput;

        // Write controllerLogFile
        for(pid_t runningAppPid : runningApps) 
        {
            registeredApps[runningAppPid]->lock();
            registeredApps[runningAppPid]->readTicks();
            long double requestedThroughput = registeredApps[runningAppPid]->data->requested_throughput;
            struct ticks ticks = registeredApps[runningAppPid]->getWindowTicks();
            long double currThroughput = getWindowThroughput(ticks);
            currentThroughput[runningAppPid] = currThroughput;
            registeredApps[runningAppPid]->unlock();
            
            controllerLogFile << cycle << ","
                << registeredApps[runningAppPid]->descriptor.pid << ","
                << registeredApps[runningAppPid]->descriptor.name << ","
                << requestedThroughput << ","
                << currThroughput << std::endl;
        }

        Frequency::CPU_FRQ currCpuFreq = Frequency::getCurrCpuFreq();
        Frequency::GPU_FRQ currGpuFreq = Frequency::getCurrGpuFreq();
        std::vector<int> utilizations = utilization.computeUtilization();
        sensors.readSensors();
        float socW = sensors.getSocW();
        float cpuW = sensors.getCpuW();
        float gpuW = sensors.getGpuW();

        // Write sensorLogFile
        {
            sensorLogFile << cycle << ",";
            for(unsigned i = 0; i < nCores; ++i)
                sensorLogFile << utilizations[i] << ",";
            sensorLogFile 
                << currCpuFreq << ","
                << currGpuFreq << ","
                << socW << ","
                << cpuW << ","
                << gpuW << std::endl;
        }

        //instert new apps
        std::vector<pid_t> newAppsVec(registerNewApps());
        std::copy(newAppsVec.begin(),newAppsVec.end(), std::inserter(newRegisteredApps, newRegisteredApps.end()));    
        runningApps.insert(newRegisteredApps.begin(), newRegisteredApps.end());

        //write outgoing message
        std::ostringstream messageToSend;
        messageToSend << "SYSTEM:" 
            << static_cast<int>(currCpuFreq) << "," 
            << static_cast<int>(currGpuFreq) << ","
            << cpuW + gpuW << "\n";

        messageToSend << "APPS:";
        for(auto appPid : runningApps){

            messageToSend 
                << appPid << ","
                << registeredApps[appPid]->descriptor.name << "," //the name should include the size somehow
                << registeredApps[appPid]->descriptor.max_threads << ","
                << registeredApps[appPid]->descriptor.gpu_implementation << ","
                << registeredApps[appPid]->descriptor.approximate_application << ","
                << static_cast<double>(registeredApps[appPid]->data->requested_throughput) << ","
                << registeredApps[appPid]->data->minimum_precision << ","
                << static_cast<double>(currentThroughput[appPid]) << ","
                << registeredApps[appPid]->data->use_gpu << ","
                << registeredApps[appPid]->data->n_cpu_cores  << ";";
        }
        std::cout << messageToSend.str() << "\n" << std::endl;

        newRegisteredApps.clear();
        unlock();
    }
}
