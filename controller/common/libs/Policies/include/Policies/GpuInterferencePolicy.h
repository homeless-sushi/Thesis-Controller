#include <fstream>
#include <set>
#include <string>

#include <sys/types.h>

#include "AppRegisterServer/Policy.h"

namespace Policy
{
    class GpuInterferencePolicy : public Policy
    {
        private:
            std::set<pid_t> newRegisteredApps; /**< Apps that have been added this cycle */
            std::set<pid_t> runningApps;       /**< Apps that have been running */
            
            std::fstream controllerLogFile;
            
        public:
            GpuInterferencePolicy(
                unsigned int nCores,
                std::string controllerLogUrl
            );

            void run(int cycle) override;
    };
}