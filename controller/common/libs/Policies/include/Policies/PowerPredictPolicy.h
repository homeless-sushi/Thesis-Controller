#ifndef POLICIES_POWER_PREDICT_POLICY_H
#define POLICIES_POWER_PREDICT_POLICY_H

#include <fstream>
#include <map>
#include <set>
#include <string>

#include <sys/types.h>

#include "Utils/ConfigInfo.h"

#include "AppRegisterServer/Policy.h"
#include "AppRegisterServer/Sensors.h"
#include "AppRegisterServer/Utilization.h"
#include "AppRegisterServer/Frequency.h"

namespace Policy
{
    class PowerPredictPolicy : public Policy
    {
        private:
            std::set<pid_t> newRegisteredApps; /**< Apps that have been added this cycle */
            std::set<pid_t> runningApps;       /**< Apps that have been running */
            
            std::fstream controllerLogFile;

            Utilization::Utilization utilization;

            Sensors::Sensors sensors;
            std::fstream sensorLogFile;

            ConfigInfo::ConfigInfo config;

        public:
            PowerPredictPolicy(
                unsigned nCores,
                std::string controllerLogUrl,
                std::string sensorsLogUrl,
                std::string configFileUrl
            );

            void run(int cycle) override;
    };
}

#endif //POLICIES_POWER_PREDICT_POLICY_H