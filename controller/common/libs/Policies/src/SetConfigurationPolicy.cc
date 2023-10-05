#include "Policies/SetConfigurationPolicy.h"

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
    SetConfigurationPolicy::SetConfigurationPolicy(
        unsigned nCores,
        std::string controllerLogUrl,
        std::string sensorsLogUrl,
        std::string configFileUrl
    ) :
        Policy(nCores),
        controllerLogFile(controllerLogUrl, controllerLogFile.out),
        utilization(nCores),
        sensorLogFile(sensorsLogUrl, sensorLogFile.out),
        config(readConfig(configFileUrl))
    {
        Frequency::SetCpuFreq(config.getCpuFrq());
        Frequency::SetGpuFreq(config.getGpuFrq());

        controllerLogFile << "CYCLE,PID,NAME,TARGET,CURRENT" << std::endl;

        sensorLogFile << "CYCLE,";
        for(unsigned i = 0; i < nCores; ++i)
            sensorLogFile << "UTILIZATION_" << i << ",";
        sensorLogFile << "CPUFREQ,GPUFREQ,SOCW,CPUW,GPUW" << std::endl;
    };


    SetConfigurationPolicy::Config SetConfigurationPolicy::readConfig(std::string configFileUrl)
    {
        std::ifstream configFile(configFileUrl);
    
        std::string lineString;
        getline(configFile, lineString);
        std::istringstream firstLineStream(lineString);
        unsigned int cpuFrq;
        firstLineStream >> cpuFrq;
        unsigned int gpuFrq;
        firstLineStream >> gpuFrq;
        
        std::map<std::string, Config::AppConfig> configs;
        while(configFile.good()){

            getline(configFile, lineString);
            std::istringstream lineStream(lineString);
            std::string name;
            lineStream >> name;
            bool gpu;
            lineStream >> gpu;
            std::vector<int> cores;
            while(lineStream.good()){

                int core;
                lineStream >> core;
                cores.push_back(core);
            }
            configs[name] = Config::AppConfig(gpu, cores);
        }

        configFile.close();

        return Config(
            static_cast<Frequency::CPU_FRQ>(cpuFrq), 
            static_cast<Frequency::GPU_FRQ>(gpuFrq), 
            std::move(configs));
    }

    void SetConfigurationPolicy::run(int cycle)
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
            AppData::setRegistered(registeredApps[newAppPid]->data, true);
            Config::AppConfig& newAppConfig =
                config.getAppConfig(std::string(registeredApps[newAppPid]->descriptor.name));
            AppData::setUseGpu(registeredApps[newAppPid]->data, newAppConfig.gpu);
            CGroupUtils::UpdateCpuSet(newAppPid, newAppConfig.cores);
            AppData::setNCpuCores(registeredApps[newAppPid]->data, newAppConfig.cores.size());
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

        sensors.readSensors();
        std::vector<int> utilizations = utilization.computeUtilization();

        sensorLogFile 
            << cycle << ",";
        for(unsigned i = 0; i < nCores; ++i)
                sensorLogFile << utilizations[i] << ",";
        sensorLogFile << Frequency::getCurrCpuFreq() << ","
            << Frequency::getCurrGpuFreq() << ","
            << sensors.getSocW() << ","
            << sensors.getCpuW() << ","
            << sensors.getGpuW() << std::endl;

        runningApps.insert(newRegisteredApps.begin(), newRegisteredApps.end());
        newRegisteredApps.clear();

        unlock();
    }
}