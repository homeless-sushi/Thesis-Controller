#include <set>

#include <sys/types.h>

#include "AppRegisterServer/Policy.h"

namespace Policy
{
    class DummyPolicy : public Policy
    {
        private:
            std::set<pid_t> newRegisteredApps; /**< Apps that have been added this cycle */
            std::set<pid_t> runningApps;       /**< Apps that have been running */
        public:
            using Policy::Policy;
            void run(int cycle) override;
    };
}