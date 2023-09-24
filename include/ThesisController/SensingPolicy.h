#include <fstream>
#include <set>
#include <string>

#include <sys/types.h>

#include "AppRegisterServer/Policy.h"
#include "AppRegisterServer/Sensors.h"
#include "AppRegisterServer/Utilization.h"

namespace Policy
{
    class SensingPolicy : public Policy
    {
        private:
            std::set<pid_t> newRegisteredApps; /**< Apps that have been added this cycle */
            std::set<pid_t> runningApps;       /**< Apps that have been running */
            
            Sensors::Sensors sensors;
            std::fstream sensorLogFile;
            unsigned nFreqSamples;
            unsigned currFreqSamples = 0;

            Utilization::Utilization utilization;

        public:
            SensingPolicy(
                unsigned nCores,
                unsigned nFreqSamples,
                std::string sensorsLogUrl);

            void run(int cycle) override;
    };
}