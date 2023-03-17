#include "ThesisController/DummyPolicy.h"

#include <iostream>
#include <iterator>
#include <memory>
#include <set>

#include "AppRegisterServer/App.h"
#include "AppRegisterServer/AppData.h"
#include "AppRegisterServer/Policy.h"

namespace Policy
{
    void DummyPolicy::run(int cycle)
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
        unlock();

        std::cout << "Cycle #" << cycle << std::endl;

        for(pid_t deregisteredApp : deregisteredApps){
            runningApps.erase(deregisteredApp);
        }

        for(auto newAppPid : newRegisteredApps){
            registeredApps[newAppPid]->lock();
            AppData::setRegistered(registeredApps[newAppPid]->data, true);
            registeredApps[newAppPid]->unlock();
        }

        int i = 0;
        for(pid_t runningAppPid : runningApps) 
        {
            registeredApps[runningAppPid]->lock();
            std::cout << "\tApp #" << i << ":" << registeredApps[runningAppPid]->descriptor.name << std::endl;
            registeredApps[runningAppPid]->readTicks();
            struct ticks ticks = registeredApps[runningAppPid]->getWindowTicks();
            long double throughput = getWindowThroughput(ticks);
            std::cout << "\t\t" << "throughput is: " << throughput << std::endl;
            registeredApps[runningAppPid]->unlock();
            i++;
        }

        runningApps.insert(newRegisteredApps.begin(), newRegisteredApps.end());
        newRegisteredApps.clear();
    }
}