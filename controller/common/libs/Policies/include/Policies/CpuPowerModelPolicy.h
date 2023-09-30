#include <fstream>
#include <set>
#include <string>

#include <sys/types.h>

#include "AppRegisterServer/Policy.h"
#include "AppRegisterServer/Sensors.h"
#include "AppRegisterServer/Utilization.h"

namespace Policy
{
    class CpuPowerModelPolicy : public Policy
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

        public:
            CpuPowerModelPolicy(
                unsigned nCores,
                std::string controllerLogUrl,
                unsigned nFreqSamples,
                std::string sensorsLogUrl);

            void run(int cycle) override;
    };
}