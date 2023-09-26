#include <optional>
#include <set>

#include <sys/types.h>

#include "AppRegisterServer/Policy.h"

namespace Policy
{
    class ExamplePolicy : public Policy
    {
        private:
            std::set<pid_t> newRegisteredApps; /**< Apps that have been added this cycle */
            std::set<pid_t> runningApps;       /**< Apps that have been running */
            
        public:
            ExamplePolicy(unsigned int nCores);

            void run(int cycle) override;
    };
}