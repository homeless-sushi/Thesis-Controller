#include <fstream>
#include <set>
#include <string>

#include <sys/types.h>

#include "AppRegisterServer/Policy.h"
#include "AppRegisterServer/Sensors.h"
#include "AppRegisterServer/Utilization.h"

namespace Policy
{
    class CpuProfilingPolicy : public Policy
    {
        private:
            std::set<pid_t> newRegisteredApps; /**< Apps that have been added this cycle */
            std::set<pid_t> runningApps;       /**< Apps that have been running */
            
            std::fstream controllerLogFile;

            Utilization::Utilization utilization;

            Sensors::Sensors sensors;
            std::fstream sensorLogFile;
            unsigned nFreqSamples;
            unsigned currFreqSamples = 0;


            pid_t appPid;
            std::vector<int> currentCpus{0};
            int nextCpu = 1;
            
        public:
            CpuProfilingPolicy(
                unsigned nCores,
                std::string controllerLogUrl,
                unsigned nFreqSamples,
                std::string sensorsLogUrl);

            void run(int cycle) override;
    };
}