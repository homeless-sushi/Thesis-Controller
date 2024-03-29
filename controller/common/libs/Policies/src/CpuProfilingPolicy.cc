#include "Policies/CpuProfilingPolicy.h"

#include <iostream>
#include <iterator>
#include <memory>
#include <set>
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
    CpuProfilingPolicy::CpuProfilingPolicy(
        unsigned nCores,
        std::string controllerLogUrl,
        unsigned nFreqSamples,
        std::string sensorsLogUrl
    ) :
        Policy(nCores),
        controllerLogFile(controllerLogUrl, controllerLogFile.out),
        utilization(nCores),
        nFreqSamples(nFreqSamples),
        sensorLogFile(sensorsLogUrl, sensorLogFile.out)
    {
        Frequency::SetCpuFreq(Frequency::getMinCpuFreq());
        Frequency::SetGpuFreq(Frequency::getMinGpuFreq());

        controllerLogFile << "CYCLE,PID,NAME,TARGET,CURRENT" << std::endl;

        sensorLogFile << "CYCLE,";
        for(unsigned i = 0; i < nCores; ++i)
            sensorLogFile << "UTILIZATION_" << i << ",";
        sensorLogFile << "CPUFREQ,GPUFREQ,SOCW,CPUW,GPUW" << std::endl;
    };

    void CpuProfilingPolicy::run(int cycle)
    {
        lock();

        std::vector<pid_t> deregisteredApps;
        std::vector<pid_t> tmp;

        tmp = deregisterDetachedApps();
        deregisteredApps.insert(std::end(deregisteredApps), std::begin(tmp), std::end(tmp));

        tmp = deregisterDeadApps();
        deregisteredApps.insert(std::end(deregisteredApps), std::begin(tmp), std::end(tmp));

        tmp = registerNewApps();
        std::copy(tmp.begin(),tmp.end(), std::inserter(newRegisteredApps, newRegisteredApps.end()));

        for(pid_t deregisteredApp : deregisteredApps){
            runningApps.erase(deregisteredApp);
        }

        for(auto newAppPid : newRegisteredApps){
            registeredApps[newAppPid]->lock();
            appPid = newAppPid;
            AppData::setRegistered(registeredApps[newAppPid]->data, true);
            CGroupUtils::UpdateCpuSet(newAppPid, currentCpus);
            registeredApps[newAppPid]->unlock();
        }

        for(pid_t runningAppPid : runningApps) 
        {
            registeredApps[runningAppPid]->lock();
            registeredApps[runningAppPid]->readTicks();
            long double requestedThroughput = registeredApps[runningAppPid]->data->requested_throughput;
            struct ticks ticks = registeredApps[runningAppPid]->getWindowTicks();
            long double currThroughput = getWindowThroughput(ticks);
            
            controllerLogFile << cycle << ","
                << registeredApps[runningAppPid]->descriptor.pid << ","
                << registeredApps[runningAppPid]->descriptor.name << ","
                << requestedThroughput << ","
                << currThroughput << std::endl;

            registeredApps[runningAppPid]->unlock();
        }

        if(!runningApps.empty()){
            sensors.readSensors();
            std::vector<int> utilizations = utilization.computeUtilization();
            Frequency::CPU_FRQ currCpuFreq = Frequency::getCurrCpuFreq();
            
            sensorLogFile 
                << cycle << ",";
            for(unsigned i = 0; i < nCores; ++i)
                    sensorLogFile << utilizations[i] << ",";
            sensorLogFile << currCpuFreq << ","
                << Frequency::getCurrGpuFreq() << ","
                << sensors.getSocW() << ","
                << sensors.getCpuW() << ","
                << sensors.getGpuW() << std::endl;

            ++currFreqSamples;
            if(!(currFreqSamples<nFreqSamples)){
                currFreqSamples = 0;

                Frequency::CPU_FRQ nextCpuFreq = Frequency::getNextCpuFreq(currCpuFreq);
                if(nextCpuFreq == currCpuFreq){
                    nextCpuFreq = Frequency::getMinCpuFreq();

                    if(nextCpu < nCores){
                        currentCpus.push_back(nextCpu);
                        nextCpu++;
                    }
                    CGroupUtils::UpdateCpuSet(appPid, currentCpus);
                    AppData::setNCpuCores(registeredApps[appPid]->data, currentCpus.size());
                }

                Frequency::SetCpuFreq(nextCpuFreq);
            }
        }

        runningApps.insert(newRegisteredApps.begin(), newRegisteredApps.end());
        newRegisteredApps.clear();

        unlock();
    }
}