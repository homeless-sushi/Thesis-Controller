#include "Policies/GpuInterferencePolicy.h"

#include <fstream>
#include <iostream>
#include <iterator>
#include <memory>
#include <set>
#include <string>
#include <vector>

#include "AppRegisterServer/App.h"
#include "AppRegisterServer/AppData.h"
#include "AppRegisterServer/Policy.h"
#include "AppRegisterServer/CGroupUtils.h"

namespace Policy
{
    GpuInterferencePolicy::GpuInterferencePolicy(
        unsigned int nCores,
        std::string controllerLogUrl
    ) : 
        Policy(nCores),
        controllerLogFile(controllerLogUrl, controllerLogFile.out)
    {
        controllerLogFile << "CYCLE,PID,NAME,TARGET,CURRENT" << std::endl;
    };

    void GpuInterferencePolicy::run(int cycle)
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

        int currentCpu = 0;
        for(auto newAppPid : newRegisteredApps){
            registeredApps[newAppPid]->lock();
            AppData::setRegistered(registeredApps[newAppPid]->data, true);
            AppData::setUseGpu(registeredApps[newAppPid]->data, true);
            CGroupUtils::UpdateCpuSet(newAppPid, std::vector<int>{currentCpu});
            currentCpu = (++currentCpu)%nCores;
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

        runningApps.insert(newRegisteredApps.begin(), newRegisteredApps.end());
        newRegisteredApps.clear();

        unlock();
    }
}
