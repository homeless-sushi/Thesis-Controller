#ifndef FINALPOLICY_FINALPOLICY_H
#define FINALPOLICY_FINALPOLICY_H

#include <fstream>
#include <set>
#include <string>

#include <sys/types.h>

#include "AppRegisterServer/Policy.h"
#include "AppRegisterServer/Sensors.h"
#include "AppRegisterServer/Utilization.h"

namespace Policy
{
    class FinalPolicy : public Policy
    {
        private:
            std::set<pid_t> newRegisteredApps; /**< Apps that have been added this cycle */
            std::set<pid_t> runningApps;       /**< Apps that have been running */
            
            std::fstream controllerLogFile;
            std::fstream sensorLogFile;

            Utilization::Utilization utilization;
            Sensors::Sensors sensors;
            
        public:
            FinalPolicy(
                unsigned nCores,
                std::string controllerLogUrl,
                std::string sensorsLogUrl);

            ~FinalPolicy() override = default;

            void run(int cycle) override;
    };
}

#endif //FINALPOLICY_FINALPOLICY_H