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

        std::vector<pid_t> deregisteredApps;

        std::vector<pid_t> detachedApps(deregisterDetachedApps());
        deregisteredApps.insert(std::end(deregisteredApps), std::begin(detachedApps), std::end(detachedApps));

        std::vector<pid_t> deadApps(deregisterDeadApps());
        deregisteredApps.insert(std::end(deregisteredApps), std::begin(deadApps), std::end(deadApps));

        std::vector<pid_t> newAppsVec(registerNewApps());
        std::copy(newAppsVec.begin(),newAppsVec.end(), std::inserter(newRegisteredApps, newRegisteredApps.end()));

        for(pid_t deregisteredApp : deregisteredApps){
            runningApps.erase(deregisteredApp);
        }

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

        runningApps.insert(newRegisteredApps.begin(), newRegisteredApps.end());

        zmqpp::message messageToSend;
        messageToSend << "SYSTEM:" 
            << static_cast<int>(currCpuFreq) << "," 
            << static_cast<int>(currGpuFreq) << ","
            << cpuW + gpuW << "\n";

        messageToSend << "APPS:";
        bool firstApp = true;
        for(auto appPid : runningApps){

            if(firstApp) {
                firstApp = false;
            } else {
                messageToSend << ";";
            }

            messageToSend 
                << appPid
                << registeredApps[appPid]->descriptor.name 
                << static_cast<double>(registeredApps[appPid]->data->requested_throughput)
                << static_cast<double>(currentThroughput[appPid])
                << static_cast<int>(registeredApps[appPid]->data->use_gpu)
                << registeredApps[appPid]->data->n_cpu_cores;
        }
        socket.send(messageToSend);

        std::string replyBuffer;
        socket.receive(replyBuffer);
        std::istringstream replyStream(replyBuffer);
        std::string typeLine;
        std::getline(replyStream, typeLine, '\n');
        std::string systemLine;
        std::getline(replyStream, systemLine, '\n');
        std::string appsLine;
        std::getline(replyStream, appsLine, '\n');

        std::istringstream systemStream(systemLine);
        std::string tmp;
        char separator;
        unsigned int newCpuFreq;
        unsigned int newGpuFreq;
        unsigned int newPow;
        std::getline(systemStream, tmp, ':') 
            >> newCpuFreq >> separator 
            >> newGpuFreq >> separator
            >> newPow;
        Frequency::SetCpuFreq(static_cast<Frequency::CPU_FRQ>(newCpuFreq));
        Frequency::SetGpuFreq(static_cast<Frequency::GPU_FRQ>(newGpuFreq));

        int currentCpu = 0;
        std::istringstream appsStream(appsLine);
        std::getline(appsStream, tmp, ':');
        while(std::getline(appsStream, tmp, ';')){

            std::istringstream appLine(tmp);
            unsigned int pidInt;
            std::string name;
            unsigned int size;
            float minimumThroughput;
            unsigned int gpuInt;
            unsigned int nCores;

            appLine >> pidInt >> separator;
            std::getline(appLine, name, ',');
            appLine
                >> size >> separator
                >> minimumThroughput >> separator
                >> gpuInt >> separator
                >> nCores;

            pid_t pid =  static_cast<pid_t>(pidInt);
            bool gpu = static_cast<bool>(gpuInt);

            registeredApps[pid]->lock();
            if (std::find(newRegisteredApps.begin(), newRegisteredApps.end(), pid) != newRegisteredApps.end()) {
                AppData::setRegistered(registeredApps[pid]->data, true);
            }
            std::vector<int> cores{};
            for (int i = 0; i < nCores; i++){
                currentCpu++;
                cores.push_back(currentCpu);
            }
            CGroupUtils::UpdateCpuSet(pid, cores);
            AppData::setNCpuCores(registeredApps[pid]->data, cores.size());
            AppData::setUseGpu(registeredApps[pid]->data, gpu);
            registeredApps[pid]->unlock();
        }

        newRegisteredApps.clear();
        unlock();
    }
}
