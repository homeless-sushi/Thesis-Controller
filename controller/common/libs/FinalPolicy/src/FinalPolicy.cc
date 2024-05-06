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

#include <zmqpp/zmqpp.hpp>

namespace Policy
{
    FinalPolicy::FinalPolicy(
        unsigned nCores,
        std::string controllerLogUrl,
        std::string sensorsLogUrl,
        std::string serverEndpoint
    ) :
        Policy(nCores),
        controllerLogFile(controllerLogUrl, controllerLogFile.out),
        utilization(nCores),
        sensorLogFile(sensorsLogUrl, sensorLogFile.out),
        context(),
        socket(context, zmqpp::socket_type::req)
    {
        //Frequency::SetCpuFreq(Frequency::getMinCpuFreq());
        //Frequency::SetGpuFreq(Frequency::getMinGpuFreq());

        socket.connect(serverEndpoint);

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
        socket.send(messageToSend.str());

        //read incoming system message
        std::string replyBuffer;
        socket.receive(replyBuffer);
        std::istringstream replyStream(replyBuffer);
        std::string systemLine;
        std::getline(replyStream, systemLine, '\n');
        std::string appsLine;
        std::getline(replyStream, appsLine, '\n');
        std::istringstream systemLineStream(systemLine);
        std::string systemPrefix;
        char separator;
        unsigned int newCpuFreq;
        unsigned int newGpuFreq;
        unsigned int newPow;
        std::getline(systemLineStream, systemPrefix, ':') 
            >> newCpuFreq >> separator 
            >> newGpuFreq >> separator
            >> newPow;
        Frequency::SetCpuFreq(static_cast<Frequency::CPU_FRQ>(newCpuFreq));
        Frequency::SetGpuFreq(static_cast<Frequency::GPU_FRQ>(newGpuFreq));
        int currentCpu = 0;
        std::istringstream appsLineStream(appsLine);
        std::string appsPrefix;
        std::getline(appsLineStream, appsPrefix, ':');
        std::string currAppInfo;
        while(std::getline(appsLineStream, currAppInfo, ';')){
            std::istringstream currAppLineStream(currAppInfo);
            pid_t appPid;
            std::string name;
            unsigned int size;
            unsigned int maxCpuCores;
            bool isGpu;
            bool isApproximate;
            float minimumThroughput;
            unsigned int minimumPrecision;
            float currentThroughput;
            bool onGpu;
            unsigned int nCpuCores;
            currAppLineStream >> appPid >> separator;
            std::getline(currAppLineStream, name, ',');
            currAppLineStream >> size >> separator
                >> maxCpuCores >> separator
                >> isGpu >> separator
                >> isApproximate >> separator
                >> minimumThroughput >> separator
                >> minimumPrecision >> separator
                >> currentThroughput >> separator
                >> onGpu >> separator
                >> nCpuCores;
            registeredApps[appPid]->lock();
            if (std::find(newRegisteredApps.begin(), newRegisteredApps.end(), appPid) != newRegisteredApps.end()) {
                AppData::setRegistered(registeredApps[appPid]->data, true);
            }
            std::vector<int> cores{};
            for (int i = 0; i < nCpuCores; i++){
                cores.push_back(currentCpu);
                currentCpu++;
            }
            CGroupUtils::UpdateCpuSet(appPid, cores);
            AppData::setNCpuCores(registeredApps[appPid]->data, cores.size());
            AppData::setUseGpu(registeredApps[appPid]->data, onGpu);
            registeredApps[appPid]->unlock();
        }

        newRegisteredApps.clear();
        unlock();
    }
}
