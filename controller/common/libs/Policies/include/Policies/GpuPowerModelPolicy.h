#ifndef POLICIES_GPU_POWER_MODEL_POLICY_H
#define POLICIES_GPU_POWER_MODEL_POLICY_H

#include <fstream>
#include <set>
#include <string>

#include <sys/types.h>

#include "AppRegisterServer/Policy.h"
#include "AppRegisterServer/Sensors.h"
#include "AppRegisterServer/Utilization.h"

namespace Policy
{
    class GpuPowerModelPolicy : public Policy
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

            int currentCpu = 0;

        public:
            GpuPowerModelPolicy(
                unsigned nCores,
                std::string controllerLogUrl,
                unsigned nFreqSamples,
                std::string sensorsLogUrl);

            void run(int cycle) override;
    };
}

#endif //POLICIES_GPU_POWER_MODEL_POLICY_H